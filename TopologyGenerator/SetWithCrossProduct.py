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
        """
        print("start add")
        new_elements = [element]
        for element in new_elements:
            print("WORKING WITH:{} new elements contains:{}".format(element, new_elements))
            for other in self.set:
                combination = other.union(element)
                if combination not in self.set and combination not in new_elements:
                    new_elements.append(combination)
                    print("added NEWWW")
            self.set.add(element)
        """

    def get(self):
        return self.set