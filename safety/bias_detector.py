"""Bias detection in generated feedback."""

import re

import structlog

logger = structlog.get_logger()


class BiasDetector:
    """Detect biased language in feedback."""

    # Genuinely dismissive phrases about educational background
    DISMISSIVE_PATTERNS = [
        r"(?:bootcamp|self-taught|online\s+course)\s+(?:education|training)\s+(?:is\s+(?:insufficient|inadequate|lacks)|lacks)",
        r"(?:(?:coding\s+)?bootcamp|self-taught)\s+(?:graduates?|developers?|programmers?)\s+(?:lack|lacks|missing|can't|cannot|won't)",
        r"(?:bootcamp|coding\s+bootcamp)\s+(?:doesn't|does\s+not)\s+prepare\s+(?:you|developers?)",
        r"(?:self-taught|bootcamp)(?:\s+(?:graduates?|developers?|programmers?))?\s+(?:is|are)\s+(?:not|never)\s+(?:equal|comparable)\s+to\s+(?:university|traditional|formal)",
        r"(?:bootcamp|self-taught|online\s+course)\s+\w+\s+means\s+(?:inadequate|insufficient)",
        r"bootcamp\b.{0,60}\blacks?\s+(?:the\s+)?rigor",
    ]

    # Demographic assumptions (about age, background, identity)
    DEMOGRAPHIC_PATTERNS = [
        r"(?:young|younger|old|older|aged)\s+(?:person|people|developers?|programmers?)\s+(?:can't|cannot|won't|will\s+not)",
        r"(?:(?:person|people|developers?|programmers?)\s+from|coming\s+from)\s+(?:poor|rich|working[\s-]?class)",
        r"(?:immigrant|international|foreign)\s+developers?.*(?:can't|cannot|won't|struggle)",
        r"given\s+(?:their|his|her)\s+age\b.{0,40}\b(?:can't|cannot|won't)",
    ]

    @staticmethod
    def detect_bias(text: str) -> tuple[bool, str]:
        """Detect biased language in feedback.

        Args:
            text: Feedback text

        Returns:
            Tuple of (is_biased, reason)
        """
        # Check for dismissive language about education
        for pattern in BiasDetector.DISMISSIVE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                reason = "Dismissive language about educational background"
                logger.warning("bias_detected", reason=reason)
                return True, reason

        # Check for demographic assumptions
        for pattern in BiasDetector.DEMOGRAPHIC_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                reason = "Demographic assumptions detected"
                logger.warning("bias_detected", reason=reason)
                return True, reason

        return False, ""
