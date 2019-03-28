class SetWithCrossProduct:
    def __init__(self, max_images_combined=-1):
        self.set = set()
        self.max_images_combined = max_images_combined

    def add(self, element):
        new_sets = [element]
        for other in self.set:
            combination = other.union(element)
            if combination not in self.set:
                if self.max_images_combined == -1 or len(combination) <= self.max_images_combined:
                    new_sets.append(combination)
        for new_set in new_sets:
            self.set.add(new_set)

    def get(self):
        return self.set