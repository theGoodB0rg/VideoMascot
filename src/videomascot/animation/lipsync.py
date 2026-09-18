from __future__ import annotations
import re
from pathlib import Path
from typing import List, Optional, Tuple, Union

from videomascot.models.schema import SpeechCue

PRESTON_BLAIR_VISEMES = {
    "rest", "smile", "open_smile",
    "A_I", "E", "O", "U",
    "M_B_P", "F_V", "L_D_T_N", "W_Q"
}

# Heuristic phonetic vowel/consonant mapping for quick English estimation from text
PHONEME_MAP = {
    "a": "A_I", "i": "A_I", "y": "A_I",
    "e": "E", "ee": "E", "ea": "E",
    "o": "O", "oa": "O", "oh": "O",
    "u": "U", "oo": "U", "ou": "U",
    "m": "M_B_P", "b": "M_B_P", "p": "M_B_P",
    "f": "F_V", "v": "F_V", "ph": "F_V",
    "l": "L_D_T_N", "d": "L_D_T_N", "t": "L_D_T_N", "n": "L_D_T_N", "s": "L_D_T_N", "z": "L_D_T_N",
    "w": "W_Q", "q": "W_Q", "wh": "W_Q", "r": "W_Q"
}


def parse_vtt_timestamp(ts_str: str) -> float:
    """Parses WebVTT timestamp (HH:MM:SS.mmm or MM:SS.mmm) into seconds."""
    parts = ts_str.strip().split(":")
    if len(parts) == 3:
        h, m, s = parts
        return float(h) * 3600.0 + float(m) * 60.0 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return float(m) * 60.0 + float(s)
    return float(ts_str)


class LipSyncEngine:
    """Evaluates speech cues and determines active mouth visemes over time."""

    def __init__(
        self,
        cues: Optional[List[SpeechCue]] = None,
        default_resting_viseme: str = "smile"
    ) -> None:
        self.cues: List[SpeechCue] = sorted(cues or [], key=lambda c: c.start)
        self.default_resting_viseme = default_resting_viseme

    VOWEL_PATTERNS = [
        (re.compile(r"(oo|ou|ew|ue|u)", re.I), "U"),
        (re.compile(r"(oa|ow|oh|aw|au|o)", re.I), "O"),
        (re.compile(r"(ee|ea|ey|e)", re.I), "E"),
        (re.compile(r"(ai|ay|igh|a|i|y)", re.I), "A_I"),
    ]

    @classmethod
    def _extract_word_visemes(cls, word: str, duration: float) -> List[str]:
        """Extracts dominant syllabic vowel visemes with readable holds (>= 180ms).
        
        Conversational words (< 0.38s) hold exactly 1 dominant vowel viseme,
        eliminating sub-word consonant flickering. Long multi-syllabic words hold
        at most 2-3 visemes.
        """
        clean = re.sub(r"[^a-zA-Z]", "", word).lower()
        if not clean:
            return ["A_I"]

        # 1. Extract vowel nuclei in order of appearance
        vowel_matches = []
        for pat, viseme in cls.VOWEL_PATTERNS:
            for m in pat.finditer(clean):
                vowel_matches.append((m.start(), viseme))

        vowel_matches.sort(key=lambda x: x[0])
        filtered_vowels = []
        last_pos = -2
        for pos, v in vowel_matches:
            if pos > last_pos + 1:
                filtered_vowels.append(v)
                last_pos = pos

        if not filtered_vowels:
            filtered_vowels = ["A_I"]

        # 2. Deduplicate consecutive identical visemes
        deduped: List[str] = []
        for s in filtered_vowels:
            if not deduped or deduped[-1] != s:
                deduped.append(s)

        # 3. Budget by duration (minimum 180ms per viseme):
        # - Typical conversational words (< 0.38s): exactly 1 dominant vowel viseme
        # - Bisyllabic words (0.38s to 0.70s): at most 2 visemes
        # - Polysyllabic words (> 0.70s): at most 3 visemes
        if duration < 0.38:
            return [deduped[0]]
        elif duration <= 0.70:
            return deduped[:2]
        else:
            return deduped[:3]

    @classmethod
    def from_vtt_content(
        cls,
        vtt_text: str,
        default_resting_viseme: str = "smile",
        time_offset: float = 0.0,
    ) -> LipSyncEngine:
        """Parses WebVTT subtitle text, synthesizes timed speech cues, and bridges coarticulation."""
        cues: List[SpeechCue] = []
        time_pattern = re.compile(r"((?:\d{2}:)?\d{2}:\d{2}\.\d{3})\s*-->\s*((?:\d{2}:)?\d{2}:\d{2}\.\d{3})")
        lines = vtt_text.splitlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            match = time_pattern.search(line)
            if match:
                raw_start = parse_vtt_timestamp(match.group(1))
                raw_end = parse_vtt_timestamp(match.group(2))
                
                start_sec = raw_start - time_offset
                end_sec = raw_end - time_offset
                
                # Next non-empty lines are subtitle text
                text_lines = []
                i += 1
                while i < len(lines) and lines[i].strip() and not time_pattern.search(lines[i]):
                    clean = re.sub(r"<[^>]+>", "", lines[i].strip())
                    text_lines.append(clean)
                    i += 1
                    
                full_text = " ".join(text_lines)
                if full_text and end_sec > 0 and end_sec > start_sec:
                    cues.extend(cls._synthesize_cues_from_text(max(0.0, start_sec), end_sec, full_text))
                continue
            i += 1

        # Coarticulation bridging: bridge micro-gaps < 180ms between spoken words in continuous speech
        bridged_cues: List[SpeechCue] = []
        for cue in cues:
            if bridged_cues:
                prev_cue = bridged_cues[-1]
                gap = cue.start - prev_cue.end
                if 0.0 < gap < 0.18:
                    prev_cue.end = cue.start
            bridged_cues.append(cue)

        return cls(cues=bridged_cues, default_resting_viseme=default_resting_viseme)

    @classmethod
    def from_vtt_file(
        cls,
        vtt_path: Union[str, Path],
        default_resting_viseme: str = "smile",
        time_offset: float = 0.0,
    ) -> LipSyncEngine:
        path = Path(vtt_path)
        if not path.exists():
            return cls(cues=[], default_resting_viseme=default_resting_viseme)
        content = path.read_text(encoding="utf-8")
        return cls.from_vtt_content(content, default_resting_viseme=default_resting_viseme, time_offset=time_offset)

    @classmethod
    def _synthesize_cues_from_text(
        cls,
        start_t: float,
        end_t: float,
        text: str
    ) -> List[SpeechCue]:
        """Breaks a text span into phonetic viseme cycles proportional to syllable duration."""
        words = text.split()
        if not words:
            return []
            
        dur = end_t - start_t
        time_per_word = dur / len(words)
        cues = []
        
        for w_idx, word in enumerate(words):
            w_start = start_t + w_idx * time_per_word
            w_end = w_start + time_per_word
            word_dur = w_end - w_start
            
            clean_word = re.sub(r"[^a-zA-Z]", "", word.lower())
            if not clean_word:
                continue
                
            visemes_for_word = cls._extract_word_visemes(word, word_dur)
            step = word_dur / len(visemes_for_word)
            for v_idx, v_shape in enumerate(visemes_for_word):
                c_s = w_start + v_idx * step
                c_e = c_s + step
                cues.append(SpeechCue(start=c_s, end=c_e, viseme=v_shape, word=word))
                
        return cues

    def get_viseme_at(self, t: float) -> Tuple[str, bool]:
        """Returns (viseme_shape, is_speaking) at timestamp t in seconds."""
        for cue in self.cues:
            if cue.start <= t <= cue.end:
                return (cue.viseme, True)
            if cue.start > t:
                break
        return (self.default_resting_viseme, False)
