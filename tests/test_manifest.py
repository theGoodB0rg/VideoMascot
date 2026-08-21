import json
import pytest
from videomascot.models.manifest import MascotManifest, BoneConfig, SlotConfig
from videomascot.models.pose import PoseState


def test_mascot_manifest_validation():
    manifest_data = {
        "id": "tech_fox",
        "name": "Tech Fox Mascot",
        "canvas_size": [1000, 1000],
        "bones": {
            "root": {"position": [500, 800], "pivot": [0, 0], "z_index": 0},
            "torso": {"parent": "root", "position": [0, -150], "pivot": [0, 0], "z_index": 10},
            "head": {"parent": "torso", "position": [0, -250], "pivot": [0, 50], "z_index": 20}
        },
        "slots": {
            "body": {
                "bone": "torso",
                "default_attachment": "default",
                "attachments": {"default": "body/torso.png"}
            },
            "mouth": {
                "bone": "head",
                "default_attachment": "rest",
                "attachments": {
                    "rest": "head/mouth/rest.png",
                    "A_I": "head/mouth/A_I.png",
                    "E": "head/mouth/E.png",
                    "O": "head/mouth/O.png"
                }
            }
        },
        "viseme_slot": "mouth",
        "visemes": {
            "rest": "rest",
            "A_I": "A_I",
            "E": "E",
            "O": "O"
        }
    }
    
    manifest = MascotManifest.model_validate(manifest_data)
    assert manifest.id == "tech_fox"
    assert manifest.bones["head"].parent == "torso"
    assert manifest.slots["mouth"].attachments["A_I"] == "head/mouth/A_I.png"
    assert manifest.visemes["O"] == "O"


def test_pose_state_defaults_and_mutation():
    pose = PoseState()
    assert pose.viseme == "rest"
    assert pose.blink_progress == 0.0
    
    pose.set_joint_rotation("head", 15.0)
    assert pose.joint_rotations["head"] == 15.0
    
    pose.set_attachment("mouth", "A_I")
    assert pose.active_attachments["mouth"] == "A_I"
