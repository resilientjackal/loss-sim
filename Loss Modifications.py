
###############################################################
###############################################################
    ##########      ACO SAMPLE BUILD        ##########
    ##########                              ##########
###############################################################
###############################################################



###############################################################
                #### Loss Modifications ####
###############################################################

import numpy



class Loss_Modification:
    def __init__(self,contract,actuarial_model):
        self.LM = actuarial_model
        self.contract = contract
        self.expect_expenditure = [sum(s) for s in self.sim()]
        self.t = 0
        self.aco_quality_score = .6
        self.loss_trend_rate = 1

    def sim(self):
        return self.LM.simulation()

    def expenditure(self):
        t1= [sum(s) for s in self.sim()]
        self.modify_freq_sev()
        t2 = [sum(s) for s in self.sim()]
        self.modify_freq_sev()
        t3 = [sum(s) for s in self.sim()]

        return t1,t2,t3

    def sharings(self):
        self.modify_freq_sev()
        actual_expend = self.expenditure()
        sharings = a.list_sub(self.expect_expenditure,actual_expend[0])
        I = int(abs(self.expect_expenditure[0]/actual_expend[0][0])>1+self.contract.msr)

        return I*sharings

    def list_sub(self,x,y):
        c=[]
        i = 0
        while i < min(len(x),len(y)):
            c.append(x[i]-y[i])
            i+=1
        return c       

    def modify_freq_sev(self):
        for cohort in self.LM.cohorts:
            cohort.severity.theta = cohort.severity.theta*self.loss_trend_rate

    def final_shared_savings(self):
       
        return [ s*self.aco_quality_score*self.contract.fsr for s in self.sharings()]
        
        
        
###############################################################
                #### Distributions ####
###############################################################


class poisson:
    def __init__(self,h):
        self.model_type = 'frequency'
        self.h = h
        # h is events per year #
    def generate_time(self):
        return numpy.random.exponential(1/self.h)

class exp_class:
    def __init__(self,n):
        self.model_type = 'severity'
    def generate_number(self,n):
        if self.n>0:
            self.n-=1
            return self.inv()

class exponential(exp_class):
    def __init__(self,n,theta):
        self.model_type = 'severity'
        self.distribution = 'exponential'
        self.theta = theta
        self.n = n
        # n is tracked for PMPM projected statistics #
        
    def generate_loss(self):
        return numpy.random.exponential(self.theta)

class gamma(exp_class):
    def __init__(self,n,alpha,theta):
        self.model_type = 'severity'
        self.distribution = 'gamma'
        self.alpha = alpha
        self.theta = theta

    def generate_loss(self):        
        return numpy.random.gamma(self.alpha,self.theta)
    

class normal(exp_class):
    def __init__(self,n,mu,sigma):
        self.model_type = 'severity'
        self.distriubition = 'normal'
        self.mu = mu
        self.sigma = sigma

    def generate_loss(self):        
        return numpy.random.normal(self.mu,self.sigma)

        
###############################################################
        #### Actuarial Frequency/Severity Model ####
###############################################################


class cohort_node:
    def __init__(self, severity_node, frequency_node):
        self.severity = severity_node
        self.frequency = frequency_node

    def generate_time(self):
        return self.frequency.generate_time()

    def generate_loss(self):
        return self.severity.generate_loss()

class Actuarial_Model:
    def __init__(self):
        self.interest = 0
        self.cohorts = []
        
    def load_node(self,input_node):
        self.cohorts.append(input_node)

    def simulation(self):
        t = 0
        Sim = []
        L = []
        for cohort in self.cohorts:
            while t < 1:
                  t += cohort.generate_time()
                  Sim.append((t, cohort.generate_loss()))
            L.append(self.results(Sim))
            Sim = []
            t = 0
        return L  

    def results(self, time_loss):
        v = (1+self.interest)**-1
        return [v**s[0]*s[1] for s in time_loss]
        
        
###############################################################
                #### Contract Parameters ####
############################################################### 

class ACO_Contract_Parameters:
    def __init__(self):
        self.track = None
        self.year = None
        self.msr = None
        self.expense_trend_distribution = [.95,1]
        self.fsr = None
        self.ACOperformancedist = [.5, .1]


    def loss_cap_rate(self):
        
        value = {2:[.05,.075,.01], 3:[.15,.15,.15]}
        if self.track == 1:
            return 0
        else:
            return value[self.track][self.year-1]

    def msrt(self,n):
        ## this method linearly interpolates the value
        table = [5000,6000,7000,8000,9000,10000,15000,20000,50000,60000]
        i = 0
        while n >= table[i]:
                    i+=1
                    if i == len(table):
                            break
                        
        rate_table = {0:.039,1:.036,2:.034,3:.032,4:.031,5:.03,\
                      6:.027,7:.025,8:.022,9:.02}

        a = (n - table[i])/(table[i]-table[i+1])

        return a*rate_table[i] + (1-a)*rate_table[i+1]



###############################################################
                #### Test Code ####
############################################################### 


males_sev = exponential(100,1000)
males_freq = poisson(200)

females_sev = gamma(150,2,300)
females_freq = poisson(180)

males = cohort_node(males_sev,males_freq)
females = cohort_node(females_sev,females_freq)

Build = Actuarial_Model()
Build.load_node(males)
Build.load_node(females)

contract = ACO_Contract_Parameters()
contract.track = 2
contract.msr = contract.msrt(5600)
contract.fsr = .5


a = Loss_Modification(contract,Build)
print(a.final_shared_savings())
        

    
            


    
    
    
        

    
        
