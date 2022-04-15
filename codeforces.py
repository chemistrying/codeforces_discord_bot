import time
import requests
import json
import logging
import os
import datetime

codeforcesLog = logging.getLogger("codeforces")
codeforcesLog.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="codeforces.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
codeforcesLog.addHandler(handler)

if not os.path.exists("user_profile"):
    os.system("mkdir user_profile")

global __userDictionary
with open("watchlist.json", 'r') as f:
    __userDictionary = json.loads(f.read())["users"]

global mainWebsite
global userStatus
global userInfo
global problemsetProblems
global contestList
# mainWebiste
mainWebsite = "https://codeforces.com/api/"
# userStatus
userStatus = "user.status?handle="
# userInfo
userInfo = "user.info?handles="
# problemsetProblems
problemsetProblems = "problemset.problems"
# contestList
contestList = "contest.list"
# codeforcesProblemset
codeforcesProblemset = 0

class CONTESTS:
    contests = dict()

    def __init__(self):
        contestListJson = json.loads((requests.get(mainWebsite + contestList)).text)
        if contestListJson["status"] == "OK":
            for contest in contestListJson["result"]:
                currentContest = {
                    "id" : contest["id"],
                    "name" : contest["name"],
                    "startTime" : contest["startTimeSeconds"]
                }
                self.contests[contest["id"]] = currentContest
        
        with open("contests.json", 'w') as f:
            f.write(json.dumps(self.contests))


class PROBLEMSET:
    problemset = dict()

    def __init__(self):
        problemsetJson = json.loads((requests.get(mainWebsite + problemsetProblems)).text)
        # print(problemsetJson["status"])
        if problemsetJson["status"] == "OK":
            problems = problemsetJson["result"]["problems"]
            problemStatistics = problemsetJson["result"]["problemStatistics"]
            for i in range(len(problems)):
                problem, statistics = problems[i], problemStatistics[i]
                rating = 0
                try:
                    rating = problem["rating"]
                except:
                    rating = "No rating"
                
                currentProblem = {
                    "problemName" : problem["name"], 
                    "rating" : rating, 
                    "tags" : problem["tags"],
                    "solvedCnt" : statistics["solvedCount"]
                }
                self.problemset[str(problem["contestId"]) + problem["index"]] = currentProblem
        
        with open("problemset.json", 'w') as f:
            f.write(json.dumps(self.problemset))
            

class PROFILE:
    # profileTemplate
    with open("template\\profile.json", 'r') as f:
        profileTemplate = f.read()     
    def __init__(self, username):
        self.username = username
        codeforcesLog.info(str("Requesting " + self.username + "'s status and info."))
        statusJSON = json.loads((requests.get(mainWebsite + userStatus + self.username)).text)
        time.sleep(1)
        infoJSON = json.loads((requests.get(mainWebsite + userInfo + self.username)).text)
        codeforcesLog.info("Request finished.")
        # print(self.statusJSON["status"])
        # print(self.infoJSON["status"])
        if statusJSON["status"] == "OK" and infoJSON["status"] == "OK":
            codeforcesLog.info("Request sucessful!")

            # create the profile
            # load the profile
            self.status = statusJSON["result"]
            self.info = infoJSON["result"][0]
            profile = json.loads(self.profileTemplate)

            # fill in the info
            for s in profile:
                profile[s] = self.bitsHandling(s)
            
            # return the dictionary
            with open("user_profile\\" + self.username + ".json", 'w') as f:
                f.write(json.dumps(profile))

        else:
            codeforcesLog.warn("Handle was not valid. Unable to create a user profile.")

    def ratingAndRankFunc(self, s):
        try:
            temp = self.info[s]
        except:
            if s == "rating" or s == "maxRating":
                return 0
            else:
                return "unrated"
        return self.info[s]
    
    def solvedProblemsFunc(self):
        problems = set({})
        for problem in self.status:
            if problem["verdict"] == "OK":
                try:
                    test = problem["problem"]["contestId"]
                except:
                    continue
                problems.add(str(problem["problem"]["contestId"]) + problem["problem"]["index"])
        return list(problems)

    def solvedProblemsCountFunc(self):
        return len(self.solvedProblemsFunc())
    
    def solvedProblemsRatingsFunc(self):
        problemDifficulty = {}
        # initialisation
        for i in range(800, 3501, 100):
            problemDifficulty[str(i)] = 0
        problemDifficulty["No ratings"] = 0
        
        for problem in self.status:
            if problem["verdict"] == "OK":
                try:
                    temp = problem["problem"]["rating"]
                except:
                    problem["problem"]["rating"] = "No ratings"
                finally:
                    problemDifficulty[str(problem["problem"]["rating"])] += 1
        return problemDifficulty

    def averageSolvedProblemsRatingsFunc(self):
        ratingsDistribution = self.solvedProblemsRatingsFunc()
        sum = 0
        sumcnt = 0
        for rating in ratingsDistribution:
            if rating != "No ratings":
                sumcnt += ratingsDistribution[rating]
        if sumcnt == 0:
            return 0
        for rating in ratingsDistribution:
            if rating != "No ratings":
                sum += int(rating) / sumcnt * ratingsDistribution[rating]
        return round(sum)


    def bitsHandling(self, s):
        return {
            "handle": self.info["handle"],
            "rating": self.ratingAndRankFunc("rating"),
            "rank": self.ratingAndRankFunc("rank"),
            "maxRating": self.ratingAndRankFunc("maxRating"), 
            "maxRank": self.ratingAndRankFunc("maxRank"),
            "solvedProblemsCount": self.solvedProblemsCountFunc(),
            "solvedProblems": self.solvedProblemsFunc(), 
            "solvedProblemsRatings": self.solvedProblemsRatingsFunc(),
            "averageSolvedProblemsRatings": self.averageSolvedProblemsRatingsFunc()
        } [s]

def update():
    codeforcesLog.info("Start creating user profile...")
    for handle in __userDictionary:
        codeforcesLog.info(str("Creating " + handle + "'s profile..."))
        # print("Writing profile...")
        PROFILE(handle)
        codeforcesLog.info(str("Profile for user " + handle + " has been setup!"))
    codeforcesLog.info("All profiles have been setup!")
    codeforcesLog.info("Start updating the problemset...")
    global codeforcesProblemset
    codeforcesProblemset = PROBLEMSET()
    codeforcesLog.info("Problemset has been updated!")
    codeforcesLog.info("Getting contests info...")
    CONTESTS()
    codeforcesLog.info("Contests obtained.")

def check(handle, parameters):
    try:
        open("user_profile\\" + handle + ".json", "r")
    except:
        codeforcesLog.info("User profile doesn't exist. Attempt to create a new one.")
        PROFILE(handle)
    
    try:
        open("user_profile\\" + handle + ".json", "r")
    except:
        codeforcesLog.warning("Unable to check user " + handle + " because the handle was not valid. Returning function check with exit code 1.")
        return (1, [])

    f = open("user_profile\\" + handle + ".json", "r")

    profile = json.loads(f.read())
    result = []
    if parameters == []:
        for info in profile:
            if info == "solvedProblems" or info == "solvedProblemsRatings":
                continue
            result.append(info + ": " + str(profile[info]))
    else:
        for param in parameters:
            try:
                test = profile[param]
            except:
                codeforcesLog.info("Caught unknown parameter", param)
                result.append(param + " not found")
                continue

            if param == "solvedProblems":
                result.append(param + " cannot be accessed because of the Discord message limit.")
            result.append(param + ": " + str(profile[param]))

    codeforcesLog.info("Returning function check with exit code 0")
    return (0, result)

def info(id):
    global codeforcesProblemset
    f = open("problemset.json", 'r')
    codeforcesProblemset = json.loads(f.read())
    try:
        problemInfo = codeforcesProblemset[id]
    except:
        return (1, "")
    
    result = []
    for x in problemInfo:
        if x == "tags":
            result.append(x + ": " + ", ".join(problemInfo[x]))
        else:
            result.append(x + ": " + str(problemInfo[x]))

    return (0, result)

def contests():
    f = open("contests.json", 'r')
    contests = json.loads(f.read())
    nowTime = time.time()
    result = []
    for contest in contests:
        if contests[contest]["startTime"] - nowTime > 0:
            result.append(str(contests[contest]["id"]) + ": " + contests[contest]["name"] + 
            "\nStart Time: " + str(datetime.datetime.fromtimestamp(contests[contest]["startTime"])) + 
            "\nhttps://codeforces.com/contests/" + str(contests[contest]["id"]))
    return (0, result)

def background_task_contests():
    f = open("contests.json", 'r')
    contests = json.loads(f.read())
    nowTime = time.time()
    result = []
    for contest in contests:
        if contests[contest]["startTime"] - nowTime > 0:
            result.append((contests[contest]["startTime"], str(contests[contest]["id"])))
    return sorted(result)

def isSolved(parameters):
    try:
        open("user_profile\\" + parameters[0] + ".json", 'r')
    except:
        PROFILE(parameters[0])

    try:
        open("user_profile\\" + parameters[0] + ".json", 'r')
    except:
        return (1, [])
    
    f = open("user_profile\\" + parameters[0] + ".json", 'r')
    profile = json.loads(f.read())
    return (0, parameters[1].upper() in profile["solvedProblems"])

# print(isSolved(["DarkChemist", "1624F"]))
