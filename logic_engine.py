class KnowledgeBase:
    """Stores facts and Horn-clause rules."""

    def __init__(self):
        self.facts = set()
        self.rules = []

    def tell_fact(self, fact_string):
        """Add a fact to the knowledge base."""
        self.facts.add(fact_string)

    def tell_rule(self, premise_list, conclusion_string):
        """Add a rule as (premises, conclusion)."""
        self.rules.append(
            (premise_list, conclusion_string)
        )

    def clear_facts(self):
        """Remove current facts but keep the rules."""
        self.facts.clear()

    def forward_chain(self):
        """
        Apply Forward Chaining until no new
        facts can be inferred.
        """

        new_facts_added = True

        while new_facts_added:
            new_facts_added = False

            for premises, conclusion in self.rules:

                # Only infer if conclusion is new
                if conclusion not in self.facts:

                    # Modus Ponens:
                    # all premises must be true
                    if all(
                        premise in self.facts
                        for premise in premises
                    ):
                        self.facts.add(conclusion)

                        new_facts_added = True