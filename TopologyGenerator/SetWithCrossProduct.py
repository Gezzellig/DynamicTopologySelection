class SetWithCrossProduct:
    def __init__(self):
        self.set = set()

    def add(self, element):
        new_sets = [element]
        for other in self.set:
            combination = other.union(element)
            if combination not in self.set:
                print(combination)
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