# input vectors: S pref by util, C pref, c quota, t,
import copy, itertools, time
from collections import OrderedDict


class CollegeAdmissionsProblem:
    def __init__(self, s_pref, c_pref, c_quota, mechanism):
        self.validate_input(s_pref, c_pref, c_quota)

        self.s_pref = copy.deepcopy(s_pref)
        self.c_pref = copy.deepcopy(c_pref)
        self.c_quota = copy.deepcopy(c_quota)
        self.utility_vector = None
        self.mechanism = mechanism

        self.mechanisms = {"TCOSM": self.TCOSM}

    @staticmethod
    def validate_input(s_pref, c_pref, c_quota):
        colleges = set()
        for student, pref in s_pref.items():
            if student not in pref:
                raise KeyError(
                    f"student {student} does not have self in preference list"
                )

            for each in pref:
                if each != student:
                    colleges.add(each)

        for college, pref in c_pref.items():
            try:
                c_quota[college]
            except:
                raise KeyError(f"College {college} isn't assigned a quota")

        for each in colleges:
            try:
                c_pref[each]
            except:
                for student, pref in s_pref.items():
                    if each in pref:
                        raise KeyError(
                            f"college {each} referenced by student {student} does not exist"
                        )

    def run(self):
        matching = self.mechanisms[self.mechanism](
            self.s_pref, self.c_pref, self.c_quota
        )

        self.s_matching = matching[0]
        self.c_matching = matching[1]
        self.analyze_matching() 

    def analyze_matching(self):
        self.s_payoff_vector = self.compute_payoff_vector()
        self.is_stable()

        for school, admission in self.c_matching.items():
            if (len(admission)) < c_quota[school]:
                self.wasteful = True
            else:
                self.wasteful = False


    def is_stable(self):
        # check through all matchings of students and get items in pref that are better than it's matching
        
        # step through that list and see if a college would take that student rather than its current set. 

        for student, matched_college in self.s_matching.items():
            c_better_than_match = s_pref[student][0:s_pref[student].index(matched_college):-1]

            for college in c_better_than_match:
                # get college pref, and matching
                c_pref = self.c_pref[college]
                matching = self.c_matching[college]

                # get list of students better than any member of its current set. 
                
                    # order c_match by c_pref 
                matching.sort(key=self.offer_sorter(c_pref))
                    # get best admitted student === index 0
                if matching:
                    best_admitted_student =  matching[0]
                    # check for index of the best admitted student in college's preference list
                    if c_pref.index(best_admitted_student) > c_pref.index(student):
                        self.a_blocking_pair = (student, college)
                        self.stable = False
                        return
        self.stable = True


        pass

    def TCOSM(self, s_pref, _c_pref, c_quota):

        c_matches = {}
        s_matches = {}
        c_pref = copy.deepcopy(_c_pref)

        for key in c_pref.keys():
            c_matches[key] = []

        for key in s_pref.keys():
            s_matches[key] = key

        while self.not_reached_quota_with_proposals_left(c_quota, c_pref, c_matches):
            proposals = {}
            for college, match in c_matches.items():
                if (not match) and (len(c_pref[college])):
                    if proposals.get(c_pref[college][0], False):
                        proposals[c_pref[college][0]].append(college)
                    else:
                        proposals[c_pref[college][0]] = [college]
                    c_pref[college].pop(0)
                elif match and len(match) < c_quota[college]:
                    if proposals.get(c_pref[college][0], False):
                        proposals[c_pref[college][0]].append(college)
                    else:
                        proposals[c_pref[college][0]] = [college]
                    c_pref[college].pop(0)

            for student, offers in proposals.items():
                # list of alternative choices
                options = []
                old_match = s_matches[student]

                # add to list of options the current tentative offer if it exists
                if old_match and old_match:
                    options.append(s_matches[student])

                #  add to list of options the offers recieved in the current step
                options.extend(offers)

                options.sort(key=self.offer_sorter(s_pref[student]))
                new_match = options[0]

                s_matches[student] = new_match

                # only add to mathing if not matched to themselves and if not already in list
                if (
                    student not in c_matches.get(new_match, [])
                ) and new_match != student:
                    c_matches[new_match].append(student)

                    if (new_match != old_match) and c_matches.get(old_match, False):
                        c_matches[old_match].remove(student)
                # remove from old matching if changed

        return (
            s_matches,
            c_matches,
        )

    @staticmethod
    def offer_sorter(pref):
        def sorter(val):
            try:
                index = pref.index(val)
                return index
            except:
                return len(pref) + 1

        return sorter

    def compute_payoff_vector(self, s_pref=None):
        vector = []
        
        if s_pref == None:
            s_pref = self.s_pref

        for student, college in self.s_matching.items():
            reversed_pref = s_pref[student][::-1]

            vector.append(reversed_pref.index(college))

        return tuple(vector)

    @staticmethod
    def not_reached_quota_with_proposals_left(c_quota, c_pref, c_matches):
        for school, students in c_matches.items():
            if (len(students) < c_quota[school]) and len(c_pref[school]):
                return True
        return False

    # def is_nash_equilibrium(self, who, true_pref_list, other_strats):

    #     match = s_matching[who]
    #     payoff_with_true_preference = len(true_pref_list[who]) - 1 - true_pref_list[who].index(match)

    #     whos_strat = s_pref[who]

    #     for each in other_strats:
    #         each[who] = whos_strat




# ________________________________________________________________


s_pref = {1: ["A", "B", "C", 1], 2: ["A", "B", "C", 2], 3: ["A", "B", "C", 3]}
s_pref2 = {1: ["B", "A", "C", 1], 2: ["A", "B", "C", 2], 3: ["A", "B", "C", 3]}


c_pref = {"A": [1, 2, 3], "B": [1, 2, 3], "C": [1, 2, 3]}

c_quota = {"A": 1, "B": 1, "C": 1}

# s_pref_strat = {
#     1: ["a","b"] 
#     2: ["a", "b"]
#     3: ["a", "b"]
# }


# problem = CollegeAdmissionsProblem(s_pref_strat, c_pref, c_quota)



def pref_generator(s_list, c_list, c_quota, t):
    c_list_perm = itertools.permutations(c_list, t)
    s_prefs_product_without_self = itertools.product(*[list(c_list_perm)]*3)

    s_list_perm = list(itertools.permutations(s_list))
    c_pref_product = list(itertools.product(*[s_list_perm,]*len(c_list)))

    return ( 
        [OrderedDict({s_list[i]: list(s_pref) + [s_list[i]] for i, s_pref in enumerate(each)})for each in s_prefs_product_without_self],  
        [OrderedDict({c_list[i]: list(c_pref) for i, c_pref in enumerate(each)}) for each in c_pref_product],     
        {each:c_quota[i] for i, each in enumerate(c_list)}
        )
    
    # cut down s_pref to quota

    # returns tuple of all possible s_pref, c_pref, c_quota

def TCOSM_problem_generator(s_list, c_list, c_quota):
    problems = itertools.product(s_list,c_list)
    
    for s_prefs, c_prefs in problems:
        yield (
            s_prefs,
            c_prefs,
            c_quota
        )


thing = pref_generator([1,2,3], ["A","B","C"], (2,1,1), 3)
# iter_thing = TCOSM_problem_generator(*thing)

s_strats = thing[0] 
c_pref = {
    "A": [3,2,1],
    "B": [1,3,2],
    "C": [2,1,3]
}
s_true_pref = {
    1: ["A","B","C",1],
    2: ["B","A","C",2],
    3: ["B","C","A",3]
}

count = 0
print_array = []
for each in s_strats:
    problem = CollegeAdmissionsProblem(each, c_pref, {"A":2, "B":1,"C":1}, "TCOSM")
    problem.run()
    count += 1
    print_array.append(problem.compute_payoff_vector(s_true_pref))

    if count == 6:
        print(print_array)
        print_array = []
        count = 0

# i =0 
# wasteful = 0
# not_stable = 0
# start = time.time()
# for each in iter_thing:

#     problem = CollegeAdmissionsProblem(*, "TCOSM")
#     problem.run()
#     if problem.wasteful:
#         wasteful +=1

#     if not problem.stable:
#         not_stable +=1
#     i+= 1

# print("Wasteful: ", wasteful)    
# print("Not stable: ", not_stable)    
# print(f'simulations ran: {i} in {time.time() - start}')

# c_pref = {
#     "A": [3,2,1],
#     "B": [1,3,2],
#     "C": [2,1,3]
# }
# s_true_pref = {
#     1: ["A","B","C",1],
#     2: ["B","A","C",2],
#     3: ["B","C","A",3]
# }


# s_pref = {
#     1: ["A","B", 1],
#     2: ["A","B", 2],
#     3: ["A", "B", 3]
#     }

