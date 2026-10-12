"""Check if generated feedback is supported by retrieved context."""

import re

import structlog

logger = structlog.get_logger()

SUPPORT_THRESHOLD = 0.5


class FaithfulnessChecker:
    """Verify that feedback claims are supported by context."""

    def check(self, feedback: str, context_chunks: list[dict]) -> float:
        """Check faithfulness of feedback to context.

        Args:
            feedback: Generated feedback text
            context_chunks: Retrieved context chunks

        Returns:
            Faithfulness score 0.0-1.0 (ratio of supported claims)
        """
        if not feedback or not context_chunks:
            logger.info(
                "faithfulness_empty_input",
                has_feedback=bool(feedback),
                has_chunks=bool(context_chunks),
            )
            return 0.0

        # Extract key claims from feedback (sentences)
        claims = self._extract_claims(feedback)
        if not claims:
            logger.info("faithfulness_no_claims_extracted")
            return 0.5  # Default to neutral if no extractable claims

        # Concatenate context text
        context_text = " ".join([chunk.get("text", "") for chunk in context_chunks])

        # Score each claim by the share of its content words the context backs
        ratios = [
            ratio
            for claim in claims
            if (ratio := self._support_ratio(claim, context_text)) is not None
        ]
        if not ratios:
            logger.info("faithfulness_no_checkable_claims")
            return 0.5  # Same neutral default as when no claims are extracted

        supported = sum(1 for ratio in ratios if ratio >= SUPPORT_THRESHOLD)
        score = sum(ratios) / len(ratios)

        logger.info(
            "faithfulness_checked", claims_count=len(claims), supported_count=supported, score=score
        )

        return score

    @staticmethod
    def _extract_claims(text: str) -> list[str]:
        """Extract key claims from feedback text.

        Args:
            text: Feedback text

        Returns:
            List of claims (sentences)
        """
        # Split by sentence (simple regex)
        sentences = re.split(r"[.!?]+", text)
        claims = [s.strip() for s in sentences if len(s.split()) >= 2]
        return claims[:10]  # Limit to 10 claims for scoring

    @classmethod
    def _is_supported(cls, claim: str, context: str) -> bool:
        """Check if a claim is supported by context.

        Args:
            claim: Claim text
            context: Context text

        Returns:
            True if claim is supported
        """
        ratio = cls._support_ratio(claim, context)
        return ratio is not None and ratio >= SUPPORT_THRESHOLD

    @classmethod
    def _support_ratio(cls, claim: str, context: str) -> float | None:
        """Share of a claim's content words that appear in the context.

        Args:
            claim: Claim text
            context: Context text

        Returns:
            Ratio 0.0-1.0, or None if the claim has no content words to check
        """
        claim_tokens = cls._content_tokens(claim)
        if not claim_tokens:
            return None
        context_tokens = cls._content_tokens(context)
        return len(claim_tokens & context_tokens) / len(claim_tokens)

    @staticmethod
    def _content_tokens(text: str) -> set[str]:
        """Tokenize text into the words a claim is checked on.

        Args:
            text: Claim or context text

        Returns:
            Lowercase words with punctuation, stop words, and generic words removed
        """
        tokens = set(re.findall(r"[a-z0-9+#]+", text.lower()))
        # Filter out common stop words
        stop_words = {
            "a",
            "an",
            "the",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "and",
            "or",
            "but",
            "in",
            "of",
            "to",
            "for",
            "that",
        }
        # Example: "The developer has strong Python and Django skills." is checked
        # on {"python", "django"} only.
        generic_words = {
            "developer",
            "candidate",
            "has",
            "have",
            "shows",
            "show",
            "knows",
            "know",
            "knowledge",
            "expert",
            "expertise",
            "experience",
            "experienced",
            "skilled",
            "skill",
            "skills",
            "strong",
        }
        return tokens - stop_words - generic_words
