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
