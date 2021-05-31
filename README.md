# Mutta-Puffs
video demo link: https://youtu.be/xBOh85lMZdw

Mutta Puffs is a sports league scheduler automated on thousands of computers from decentralized market of computational power in Golem. 

# Background
Golem (https://www.golem.network/) is a network that provides access to computational power and storage capacity of thousands of computers through the Internet. These resources can be accessed by paying a rent to the providers who provide these resources directly. Tasks can be split up into independent sub-tasks and sent to multiple providers on Golem for parallel computation. In such a scenario, a very important use-case arises: Solving a search problem by dividing the search space into independent chunks and searching for a optimal solution in each of those divided search spaces parallely. The Travelling Tournament Problem is one such problem which has been proven to be NP-Complete under tight constraints. 

# What Does Mutta Puffs do?
The purpose of Mutta Puffs is to solve the Travelling Tournament Problem for a given set of teams using Population-based Simulated Annealing, which is an algorithm proposed by Van Hentenryck, Pascal, and Yannis Vergados in their paper "Population-based simulated annealing for traveling tournaments." at Proceedings of the National Conference on Artificial Intelligence. The paper can be accessed through this link: https://www.aaai.org/Papers/AAAI/2007/AAAI07-041.pdf

# How to Interact with Mutta Puffs?
## Setting Up
Mutta Puffs runs on top of Golem. So, the following tasks are to be performed before running the python application:

1.) The dockerfile muttapuffs.docketfile has to converted into a GVM image. Make sure that you have docker and gvmkit-build installed and execute these commands while docker is running to get the gvm image:

```
docker build . -t muttapuffs
gvmkit-build muttapuffs:latest
gvmkit-build muttapuffs:latest --push
```

2.) run yagna daemon, set YAGNA_APPKEY environment variable and intitialize a payment account by following the instruction in this primer: https://handbook.golem.network/requestor-tutorials/flash-tutorial-of-requestor-development

3.) Install required packages: `pip install -r requirements.txt`

Now you are ready to talk to Mutta Puffs.

## Adding Teams

Run the program run.py
`python run.py`

A window opens and, it look like this:

![image](https://user-images.githubusercontent.com/40036742/120087809-d73e1000-c108-11eb-9201-c7e0dd9528d3.png)

All the teams that will be participating in your sports league must be added here. Since, the league is supposed to be a round-robin tournament with a team playing a home and an away game against every other team, Mutta Puffs will expect an even number of teams from you. This is necessary to ensure that every team gets a game during each round of play.

The minimum number of teams that must be provided here is 4. It is unnecessary to autamate the scheduling process for a sports league with only 2 teams. 

Once you have added your teams along with their home stadium locations, click the "GENERATE SCHEDULE" button which takes you to the next screen.

## Enter Golem

Now you will be looking at this window:

![image](https://user-images.githubusercontent.com/40036742/120087824-0d7b8f80-c109-11eb-825a-e76efa7ba236.png)

The big wihte box on the right is a plain text box in which all the events from Golem will be logged during the time of execution. 

You may interact with this screen in three ways:

1.) Compute:

The compute button in the bottom left corner runs the parallelizer.py program which connects with  required number of providers and sends them sa.py file along with an initial random schedule contained in the file schedule.txt

2.) settings:

The setting button opens the settings window which looks like this:

![image](https://user-images.githubusercontent.com/40036742/120087401-33069a00-c105-11eb-86c6-620729759278.png)

**Number of Providers:** It is the maximum of providers that you are willing to connect to. It has to be a positive integer

**Number of Iterations:** It is number of iterations(defined as waves in the original paper)  of search that has to be performed.

**Budget:** The maximum number of GLM tokens that you are willing to spend

**Network:** You may choose between mainnet and rinkeby

**Driver:** You may choose between zksync and erc20

**Subnet Tag:** The subnet tag to be used. 

**IMPORTANT:** Make sure that you use the network and driver with which the payment account was initiated. Or else, you may receive an error.

3.) Open Schedule:

This button gets activated after the process parallelizer.py has finished. The result may be a near-optimal schedule or an error. In case there was no error, clicking this button will open the file "schedule.png" in which the schedule was saved. The following image shows an example of what a schedule will look like:

![image](https://user-images.githubusercontent.com/40036742/120087536-8af1d080-c106-11eb-8664-89ed932b7e0a.png)

Note that half of the abbreviations are prefixed with "@". It means that the game is away from home. 

But, if the computation ends with an error, the user will be notified through an error message. The user may then check the errors, rectify them and recompute. However, the best schedule so far will be saved in schedule.png and the user may view them. 

# Ways to Improve Mutta-Puffs

1.) Mutta Puffs needs a better Front-End and a logo. Front-End devs and designers are always welcome to work on it and your work will be highly appreciated.

2.) The MapBox API used in the map to select home stadiums runs on free tier. It needs to be upgraded when this application scales.

3.) When thera are large number of teams involved in the league, a interface to allow bulk upload of team details through a csv file has to be developed.

4.) Disallow users from using rinkeby as it is meant for testing purposes only.
