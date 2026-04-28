"""
Challenge Engine for Randomized Liveness Verification
"""
import random
import logging
from typing import List, Dict, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ChallengeType(str, Enum):
    """Challenge types"""
    BLINK = "blink"
    HEAD_LEFT = "head_left"
    HEAD_RIGHT = "head_right"
    LOOK_UP = "look_up"
    LOOK_DOWN = "look_down"
    SMILE = "smile"
    NOD = "nod"


class ChallengeEngine:
    """Generates and validates randomized anti-spoof challenges"""
    
    CHALLENGE_INSTRUCTIONS = {
        ChallengeType.BLINK: "Please blink twice rapidly",
        ChallengeType.HEAD_LEFT: "Turn your head to the left",
        ChallengeType.HEAD_RIGHT: "Turn your head to the right",
        ChallengeType.LOOK_UP: "Look upward",
        ChallengeType.LOOK_DOWN: "Look downward",
        ChallengeType.SMILE: "Smile for the camera",
        ChallengeType.NOD: "Nod your head",
    }
    
    CHALLENGE_TIMEOUT = {
        ChallengeType.BLINK: 5,
        ChallengeType.HEAD_LEFT: 8,
        ChallengeType.HEAD_RIGHT: 8,
        ChallengeType.LOOK_UP: 6,
        ChallengeType.LOOK_DOWN: 6,
        ChallengeType.SMILE: 6,
        ChallengeType.NOD: 8,
    }
    
    def __init__(self):
        """Initialize challenge engine"""
        self.available_challenges = list(ChallengeType)
    
    def generate_challenge_sequence(
        self,
        num_challenges: int = 3
    ) -> List[Dict[str, any]]:
        """
        Generate random sequence of challenges
        
        Args:
            num_challenges: Number of challenges to generate
            
        Returns:
            List of challenge dictionaries
        """
        # Ensure num_challenges doesn't exceed available types
        num_challenges = min(num_challenges, len(self.available_challenges))
        
        # Randomly select unique challenges
        selected_challenges = random.sample(
            self.available_challenges,
            num_challenges
        )
        
        challenge_sequence = []
        for idx, challenge_type in enumerate(selected_challenges):
            challenge = {
                "id": idx + 1,
                "type": challenge_type.value,
                "instruction": self.CHALLENGE_INSTRUCTIONS[challenge_type],
                "timeout_seconds": self.CHALLENGE_TIMEOUT[challenge_type],
                "status": "pending"
            }
            challenge_sequence.append(challenge)
        
        logger.info(f"Generated challenge sequence: {[c['type'] for c in challenge_sequence]}")
        return challenge_sequence
    
    def get_challenge(
        self,
        challenge_id: int,
        challenges: List[Dict]
    ) -> Dict:
        """
        Get specific challenge
        
        Args:
            challenge_id: Challenge ID
            challenges: Challenge sequence
            
        Returns:
            Challenge dictionary
        """
        for challenge in challenges:
            if challenge["id"] == challenge_id:
                return challenge
        
        raise ValueError(f"Challenge {challenge_id} not found")
    
    def validate_challenge_response(
        self,
        challenge_type: str,
        blink_detected: bool = False,
        head_pose: str = "neutral",
        smile_detected: bool = False
    ) -> Tuple[bool, str]:
        """
        Validate user response to challenge
        
        Args:
            challenge_type: Type of challenge
            blink_detected: Whether blink was detected
            head_pose: Detected head pose
            smile_detected: Whether smile was detected
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            if challenge_type == ChallengeType.BLINK.value:
                if blink_detected:
                    return True, "Blink challenge passed"
                else:
                    return False, "No blink detected"
            
            elif challenge_type == ChallengeType.HEAD_LEFT.value:
                if head_pose == "left":
                    return True, "Head left challenge passed"
                else:
                    return False, f"Expected left, got {head_pose}"
            
            elif challenge_type == ChallengeType.HEAD_RIGHT.value:
                if head_pose == "right":
                    return True, "Head right challenge passed"
                else:
                    return False, f"Expected right, got {head_pose}"
            
            elif challenge_type == ChallengeType.LOOK_UP.value:
                if head_pose == "up":
                    return True, "Look up challenge passed"
                else:
                    return False, f"Expected up, got {head_pose}"
            
            elif challenge_type == ChallengeType.LOOK_DOWN.value:
                if head_pose == "down":
                    return True, "Look down challenge passed"
                else:
                    return False, f"Expected down, got {head_pose}"
            
            elif challenge_type == ChallengeType.SMILE.value:
                if smile_detected:
                    return True, "Smile challenge passed"
                else:
                    return False, "No smile detected"
            
            elif challenge_type == ChallengeType.NOD.value:
                # Nod is typically a head down followed by head up
                # For simplicity, we'll accept down movement as nod
                if head_pose == "down":
                    return True, "Nod challenge passed"
                else:
                    return False, f"Expected nod (down), got {head_pose}"
            
            else:
                return False, f"Unknown challenge type: {challenge_type}"
        
        except Exception as e:
            logger.error(f"Error validating challenge: {str(e)}")
            return False, str(e)
    
    def get_challenge_progress(
        self,
        challenges: List[Dict]
    ) -> Dict:
        """
        Get overall challenge progress
        
        Args:
            challenges: Challenge sequence
            
        Returns:
            Progress dictionary
        """
        total = len(challenges)
        completed = sum(1 for c in challenges if c["status"] == "completed")
        passed = sum(1 for c in challenges if c["status"] == "passed")
        failed = sum(1 for c in challenges if c["status"] == "failed")
        
        progress = {
            "total_challenges": total,
            "completed": completed,
            "passed": passed,
            "failed": failed,
            "remaining": total - completed,
            "overall_status": "pending",
            "completion_percentage": (completed / total * 100) if total > 0 else 0
        }
        
        if failed > 0:
            progress["overall_status"] = "failed"
        elif completed == total:
            progress["overall_status"] = "completed"
        elif completed > 0:
            progress["overall_status"] = "in_progress"
        
        return progress
    
    def is_challenge_sequence_passed(
        self,
        challenges: List[Dict]
    ) -> bool:
        """
        Check if all challenges in sequence were passed
        
        Args:
            challenges: Challenge sequence
            
        Returns:
            Whether all challenges passed
        """
        for challenge in challenges:
            if challenge["status"] != "passed":
                return False
        return True
