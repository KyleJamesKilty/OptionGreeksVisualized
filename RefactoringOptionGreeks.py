# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 13:43:59 2022

@author: Kyle
"""

import datetime
import math
import matplotlib.pyplot
import yfinance
from scipy.stats import norm

matplotlib.pyplot.switch_backend('TkAgg')

class StockOption:
    
    def __init__(self, optionPrice, sharePrice, strikePrice, expiration, 
                 optionType, currentTime, currentDate,
                 bidPrice, askPrice, interestRate):
        
        # Fixed Parameters
        
        self.date = currentDate
        self.time = currentTime   
        
        self.optionType = optionType.lower()
        if self.optionType == 'optioncall':
            if strikePrice > sharePrice:
                self.itm = False
            else:
                self.itm = True
        if self.optionType == 'optionput':
            if strikePrice > sharePrice:
                self.itm = True
            else:
                self.itm = False
                
        self.expiration = expiration
        self.optionPrice = round(optionPrice, 3)
        self.sharePrice = round(sharePrice, 3)
        self.strikePrice = round(strikePrice, 3)
        
        self.actualTime = self.actualTime(currentDate, currentTime, expiration)
        self.interestRate = interestRate
        self.actualInterest = interestRate
        self.dividendRate = 0
        self.bidPrice = bidPrice
        self.askPrice = askPrice 
        volatilityParam = self.BlackScholesMertonImpliedVolatility(self.sharePrice, self.actualTime)        
        self.impliedVolatility = volatilityParam[0]
        self.BSMvega = volatilityParam[1]
        
        #For debugging
        #self.impliedVolatility = 2.5
        #self.BSMvega = 0
        
        '''
        Black Scholes Model Greeks
        "The Greeks" measure the sensitivity of the value of a derivative 
        product or a financial portfolio to changes in parameter values while 
        holding the other parameters fixed
        '''
       
        
        self.BSMdelta = self.__delta()
        self.BSMgamma = self.__gamma()
        self.BSMtheta = self.__theta()
        self.BSMrho = self.__rho()
        self.BSMlambda = self.__lambda()
        self.BSMvanna = self.__vanna()
        self.BSMcharm = self.__charm()
        self.BSMvomma = self.__vomma()
        self.BSMveta = self.__veta()
        self.BSMspeed = self.__speed()
        self.BSMzomma = self.__zomma()
        self.BSMcolor = self.__color()
        self.BSMultima = self.__ultima()
        
    def __repr__(self):
        '''
        Calling information for each stock option instance
        '''
        return "{}".format(self.strikePrice)
    
    def actualTime(self, currentDate, currentTime, expiration):
        '''
        This converts the time into minutes because minutes is what the VIX model uses.
        '''
        hours, minutes = 17, 30
        years, months, days = [int(time) for time in expiration.split('-')]
        expirationDatetime = datetime.datetime(years, months, days, hours, minutes)
        
        hours, minutes = [int(time) for time in currentTime.split(':')]
        years, months, days = [int(time) for time in currentDate.split('-')]
        currentDatetime = datetime.datetime(years, months, days, hours, minutes)
        
        days = 24*60*60*(expirationDatetime - currentDatetime).days
        seconds = (expirationDatetime - currentDatetime).seconds
        
        actualTimeValue = (days + seconds) / (365*24*60*60)
        
        return actualTimeValue
    
    def N(self, x):
        
        NValue = norm.cdf(x)
        
        return NValue 
    
    def phi(self, x):
        
        phiValue = norm.pdf(x)
        
        return phiValue
    
    def d1(self, sharePrice, actualTime, impliedVolatility):
        
        strikePrice = self.strikePrice
        interestRate = self.interestRate
        dividendRate = self.dividendRate
        
        d1Value = ((math.log(sharePrice / strikePrice + 1 - 1) + (interestRate - dividendRate+ 0.5*impliedVolatility ** 2  + 1 - 1)*actualTime))/(impliedVolatility*math.sqrt(actualTime))
        
        return d1Value
    
    def d2(self, sharePrice, actualTime, impliedVolatility):
        
        d1 = self.d1(sharePrice, actualTime, impliedVolatility)
        
        d2Value = d1 - impliedVolatility*math.sqrt(actualTime)
        
        return d2Value
    
    def presentValueStrike(self, actualTime):
        
        presentValueStrikeValue = self.strikePrice * math.exp(-1 * self.interestRate * actualTime)
        
        return presentValueStrikeValue 
    
    def presentValueShare(self, sharePrice, actualTime):
        
        presentValueShareValue = sharePrice* math.exp(-1 * self.interestRate * actualTime)
        
        return presentValueShareValue
    
    def BlackScholesMertonPrice(self, sharePrice, actualTime, impliedVolatility):   
        
        if actualTime == 0:
            if self.optionType == None:
                print('Error')
                
            elif self.optionType == 'optioncall':
                selfValue = max(sharePrice - self.strikePrice, 0)
                
            elif self.opt_type == 'optionput':
                selfValue = max(self.strikePrice - sharePrice, 0)
            
            return round(selfValue, 3)
        
        elif actualTime != 0:
            if self.optionType == 'optioncall':
                Nd1 = self.N(self.d1(sharePrice, actualTime, impliedVolatility))
                Nd2 = -1 * self.N(self.d2(sharePrice, actualTime, impliedVolatility))
            
            elif self.optionType == 'optionput':
                Nd1 = -1 * self.N(-1 * self.d1(sharePrice, actualTime, impliedVolatility))
                Nd2 = self.N(-1 * self.d2(sharePrice, actualTime, impliedVolatility))
            
            return round(self.presentValueShare(sharePrice, actualTime)
                         * Nd1 + self.presentValueStrike(actualTime)
                         * Nd2  + 1 - 1, 3)
        
    def BSMvega(self, sharePrice, actualTime, impliedVolatility):
        
        vegaValue = (self.presentValueStrike(actualTime) * 
                 self.phi(self.d2(sharePrice, actualTime, impliedVolatility)) 
                 * math.sqrt(actualTime)) / 100
        
        return round(vegaValue, 4)
    
    def BlackScholesMertonImpliedVolatility(self, sharePrice, actualTime):
        
        IV_low_guess = 0
        IV_high_guess = 20
        IV_middle = (IV_low_guess + IV_high_guess) * 0.5
        priceMiddle = self.BlackScholesMertonPrice(sharePrice, actualTime, IV_middle)
        eAmount = priceMiddle - self.optionPrice
        
        while IV_high_guess - IV_low_guess >= 0.1 / 100:
            
            if eAmount > 0:
                IV_high_guess = IV_middle
            elif eAmount < 0:
                IV_low_guess = IV_middle
            elif eAmount == 0:
                break
            
            IV_middle = 0.5 * (IV_high_guess + IV_low_guess)
            priceMiddle = self.BlackScholesMertonPrice(sharePrice, actualTime, IV_middle)
            eAmount = priceMiddle - self.optionPrice
        vega = self.BSMvega(sharePrice, actualTime, IV_middle)
        return IV_middle, vega
    
    def __delta(self):
        if self.optionType == 'optionput':
            deltaValue = -self.N(-self.d1(self.sharePrice, self.actualTime, self.impliedVolatility))
        elif self.optionType == 'optioncall':
            deltaValue = self.N(self.d1(self.sharePrice, self.actualTime, self.impliedVolatility))
        
        return round(deltaValue, 4)
    
    def __gamma(self):
        
        impliedVolatility = self.impliedVolatility
        actualTime = self.actualTime
        sharePrice = self.sharePrice
        x= self.d2(sharePrice, actualTime, impliedVolatility)
        presentValueStrike = self.presentValueStrike(actualTime)
        fidtwo = self.phi(x)
        
        gammaValue = (presentValueStrike * fidtwo) / (sharePrice**2*impliedVolatility*math.sqrt(actualTime))
        
        return round(gammaValue,4)
    
    def __theta(self):
        
        impliedVolatility = self.impliedVolatility
        actualTime = self.actualTime
        sharePrice = self.sharePrice
        x = self.d1(sharePrice, actualTime, impliedVolatility)
        presentValueStrike = self.presentValueStrike(actualTime)
        presentValueShare = self.presentValueShare(sharePrice ,actualTime)
        
        if self.optionType == 'optionput':
            fidone = self.phi(-x)
            actualInterest = self.actualInterest
            dividendRate = -self.dividendRate
            Nd1 = self.N(-self.d1(sharePrice, actualTime, impliedVolatility))
            Nd2 = self.N(-self.d2(sharePrice, actualTime, impliedVolatility))
            
        elif self.optionType == 'optioncall':
            fidone = self.phi(x)
            actualInterest = self.actualInterest
            dividendRate = -self.dividendRate
            Nd1 = self.N(self.d1(sharePrice, actualTime, impliedVolatility))
            Nd2 = self.N(self.d2(sharePrice, actualTime, impliedVolatility))
            
        thetaValue = (-((presentValueShare*fidone*impliedVolatility) / (2*math.sqrt(actualTime)))
        + actualInterest*presentValueStrike*Nd2 
        + dividendRate*presentValueShare*Nd1) / 365
        
        return round(thetaValue, 4)
    
    def __rho(self):
        if self.optionType == 'optionput':
            
            rhoValue = -self.presentValueStrike(self.actualTime)*self.actualTime * self.N(-self.d2(self.sharePrice, self.actualTime, self.impliedVolatility)) / 100
            
            return round(rhoValue, 4)
             
                    
        elif self.optionType == 'optioncall':
            
            rhoValue =  self.presentValueStrike(self.actualTime)*self.actualTime*self.N(self.d2(self.sharePrice, self.actualTime, self.impliedVolatility)) / 100
            
            return round(rhoValue, 4)
        
    
    def __lambda(self):
        lambdaValue = self.BSMdelta*(self.sharePrice / self.optionPrice)
        
        return round(lambdaValue, 4)
        
    def __vanna(self):
        vannaValue = (self.optionPrice / self.sharePrice)*(1 - 
        (self.d1(self.sharePrice, self.actualTime, self.impliedVolatility)
        / (self.impliedVolatility*math.sqrt(self.actualTime))))
        
        return round(vannaValue, 4)
        
    def __charm(self):
        
        helper = (2*(self.actualInterest - self.dividendRate)*self.actualTime 
        - self.d2(self.sharePrice, self.actualTime, self.impliedVolatility)
        *self.impliedVolatility*math.sqrt(self.actualTime)) / (2*self.actualTime
        *self.impliedVolatility*math.sqrt(self.actualTime))
        x = self.d1(self.sharePrice, self.actualTime, self.impliedVolatility)
        fidone = self.phi(x)
        
        if self.optionType == "optionput":
            
            charmValue = -self.dividendRate*math.exp(-self.dividendRate*self.actualTime)*self.N(-self.d1(self.sharePrice, self.actualTime, self.impliedVolatility))- math.exp(-self.dividendRate*self.actualTime)*fidone*helper / 365
            
            return round(charmValue, 4)
        
        elif self.optionType == "optioncall":
            
            charmValue = self.dividendRate*math.exp(-self.dividendRate*self.actualTime)*self.N(self.d1(self.sharePrice, self.actualTime, self.impliedVolatility))- math.exp(-self.dividendRate*self.actualTime)*fidone*helper / 365
            
            return round(charmValue, 4)
            
    def __vomma(self):
        vommaValue = (self.BSMvega*self.d1(self.sharePrice, self.actualTime, self.impliedVolatility)*self.d2(self.sharePrice, self.actualTime, self.impliedVolatility)) / self.impliedVolatility
        
        return round(vommaValue, 4)
        
    
    def __veta(self):
        vetaValue = (-self.presentValueShare(self.sharePrice, self.actualTime)
        *self.phi(self.d1(self.sharePrice, self.actualTime, self.impliedVolatility))
        *math.sqrt(self.actualTime)*(self.dividendRate + ((self.actualInterest - self.dividendRate)
        *self.d1(self.sharePrice, self.actualTime, self.impliedVolatility)) / (self.impliedVolatility*math.sqrt(self.actualTime)) 
        - (1 + self.d1(self.sharePrice, self.actualTime, self.impliedVolatility)*self.d2(self.sharePrice, self.actualTime, self.impliedVolatility)) 
        / (2*self.actualTime))) / (100*365)
        
        return round(vetaValue, 4)
        
    def __speed(self):
        speedValue = -(self.BSMgamma / self.sharePrice)*((self.d1(self.sharePrice, self.actualTime, self.impliedVolatility) 
        / (self.impliedVolatility*math.sqrt(self.actualTime))) + 1)
        
        return round(speedValue, 4)
    
    def __zomma(self):
        zommaValue = self.BSMgamma*((self.d1(self.sharePrice, self.actualTime, self.impliedVolatility)
        *self.d2(self.sharePrice, self.actualTime, self.impliedVolatility) - 1) / self.impliedVolatility)
        
        return round(zommaValue, 4)
    
    def __color(self):
        colorValue = (-math.exp(-self.dividendRate * self.actualTime)*
        (self.phi(self.d1(self.sharePrice, self.actualTime, self.impliedVolatility))
        / (2*self.sharePrice*self.actualTime*self.impliedVolatility*math.sqrt(self.actualTime)))*(2*self.dividendRate*self.actualTime + 1 + 
        ((2*(self.actualInterest - self.dividendRate)*self.actualTime - self.d2(self.sharePrice, self.actualTime, self.impliedVolatility)
        *self.impliedVolatility*math.sqrt(self.actualTime)) / (self.impliedVolatility*math.sqrt(self.actualTime)))
        *self.d1(self.sharePrice, self.actualTime, self.impliedVolatility))) / 365
        
        return round(colorValue, 4)
                                                                                                  
    
    def __ultima(self):
        
        ultimaValue = (-self.BSMvega/(self.impliedVolatility**2))*(self.d1(self.sharePrice, self.actualTime, self.impliedVolatility)
        *self.d2(self.sharePrice, self.actualTime, self.impliedVolatility)*(1 - self.d1(self.sharePrice, self.actualTime, self.impliedVolatility)
        *self.d2(self.sharePrice, self.actualTime, self.impliedVolatility)) + self.d1(self.sharePrice, self.actualTime, self.impliedVolatility)**2 
        + self.d2(self.sharePrice, self.actualTime, self.impliedVolatility)**2)
        
        return round(ultimaValue, 4)
    
def handleDateTime():
    current = datetime.datetime.now()
    cD = str(current.date())
    cT = '{}:{}'.format(current.time().hour, current.time().minute)
    
    return cD, cT

def plotCheckandParams():
    ticker = input('Enter stock ticker:').upper()
    
    try: yfinance.Ticker(ticker).options[0]
    
    except:
        stop = 0
        
        while stop == 0:
            print('Try again')
            ticker = input('Enter stock ticker:').upper()
            try:
                yfinance.Ticker(ticker).options[0]
                stop = 1
            
            except:
                stop = 0
    parameters = ['optionPrice','impliedVolatility','BSMvega','BSMdelta','BSMgamma','BSMtheta', 'BSMlambda', 'BSMrho', 'BSMcharm', 'BSMveta', 'BSMcolor', 'BSMspeed', 'BSMvanna', 'BSMvomma', 'BSMzomma', 'BSMultima']          
    stop = 0
    
    priceType = input('Mid or Last price? [mid or last]')
    while priceType not in ['mid','last']:
        priceType = input('Mid or Last Price? [mid or last]')
        
    optionType = 'both'
    moneynessType = 'both'
    
    currentDate, currentTime = handleDateTime()
    
    return ticker, parameters, priceType, optionType, moneynessType, currentDate, currentTime

def returnOptions(currentDate, currentTime, ticker, optionType, priceType, interestRate = 0):
    
    ticker = yfinance.Ticker(ticker)
    
    sharePrice = ticker.info['regularMarketPrice']
    
    expirations = ticker.options
    
    optionCallObjects = {}
    
    optionPutObjects = {}
    
    for expiration in expirations:
        
        print('Getting Option Data for expiration of {}'.format(expiration))
        
        optionChain = ticker.option_chain(expiration)
        
        optionCalls = optionChain.calls.fillna(0)
        optionPuts = optionChain.puts.fillna(0)
        
        singleCallChain = []
        singlePutChain = []
        
        idx = 0
        while idx < len(optionCalls):
            bidPrice = optionCalls['bid'].iloc[idx]
            askPrice = optionCalls['ask'].iloc[idx]
            lastPrice = optionCalls['lastPrice'].iloc[idx]
            strikePrice = optionCalls['strike'].iloc[idx]
            
            if priceType == 'mid':
                optionPrice = round((bidPrice + askPrice)/2, 2)
            elif priceType == 'last':
                optionPrice = lastPrice
            
            singleCallChain.append(StockOption(optionPrice, sharePrice, strikePrice, expiration, 'optioncall', currentTime, currentDate, bidPrice, askPrice, interestRate))
            idx += 1
            
        idx = 0   
        while idx < len(optionPuts):
            bidPrice = optionPuts['bid'].iloc[idx]
            askPrice = optionPuts['ask'].iloc[idx]
            lastPrice = optionPuts['lastPrice'].iloc[idx]
            strikePrice = optionPuts['strike'].iloc[idx]
            
            if priceType == 'mid':
                optionPrice = round((bidPrice + askPrice)/2, 2)
            elif priceType == 'last':
                optionPrice = lastPrice
            
            singlePutChain.append(StockOption(optionPrice, sharePrice, strikePrice, expiration, 'optionput', currentTime, currentDate, bidPrice, askPrice, interestRate))
            idx += 1
        
        optionCallObjects['{} C'.format(expiration)] = singleCallChain
        
        optionPutObjects['{} P'.format(expiration)] = singlePutChain
        
    return {'callOptions': optionCallObjects, 'putOptions' : optionPutObjects}
        
    

def plotOptions(StockOptions, parameters, ticker, currentDate, currentTime):
    
    faceColor = 'white'
    figure1 = matplotlib.pyplot.figure()
    
    titles = [x for x in parameters]
    
    optionTypes = list(StockOptions.keys())
    
    firstIteration = True
    
    expirations = []
    
    a = 1
    
    mainTitle = []
    
    for optionType in optionTypes:
        if optionType == 'callOptions':
            itmColor = 'black'
            otmColor = 'yellow'
            mainTitle.append('\nITM callOptions={}, OTM callOptions={}'.format(itmColor,otmColor))
            
        elif optionType == 'putOptions':
            itmColor = 'green'
            otmColor = 'red'
            mainTitle.append('\nITM putOptions={}, OTM putOptions={}'.format(itmColor,otmColor))
    
        allExpirationsOptions = StockOptions[optionType]
    
        allChains = list(allExpirationsOptions.keys())
    
        b = 0
        
        for singleChain in allChains: #Adds all Option Expirations to a list
            
            if a == 1:
                expiration = singleChain.split(' ')[0] #Splits after first space
                expirations.append(expiration)
            
            individualStrikes = allExpirationsOptions[singleChain]
            
            idx = 2
            
            for parameter in parameters:
                tITM = []
                gITM = []
                bITM = []
                
                tOTM = []
                gOTM = []
                bOTM = []
                if firstIteration == True:
                    exec("subplot{} = figure1.add_subplot({},{},{}, projection = '3d')".format(idx - 1, 4, 4, idx - 1))
                    eval("subplot{}.set_title(titles[{}])".format(idx - 1, idx - 2))
                    eval("subplot{}.set_xlabel('strike')".format(idx - 1))
                    eval("subplot{}.view_init(0, 90)".format(idx - 1))
                
                for individualOption in individualStrikes:
                    sharePrice = individualOption.sharePrice
                    if individualOption.itm:
                        itm = True
                    else:
                        itm = False
                    
                    if itm == True:
                        tITM.append(individualOption.strikePrice)
                        gITM.append(b)
                        eval('bITM.append(individualOption.{})'.format(parameter))
                    elif itm == False:
                        tOTM.append(individualOption.strikePrice)
                        gOTM.append(b)
                        eval('bOTM.append(individualOption.{})'.format(parameter))
                  
                eval("subplot{}.plot(tITM, gITM, bITM, '{}')".format(idx - 1, itmColor))
                eval("subplot{}.plot(tOTM, gOTM, bOTM, '{}')".format(idx - 1, otmColor))
                        
                    
                idx += 1
                
            firstIteration = False
            
            b += 1
            
        a += 1
    
    if b <= 13:
        marks = [x for x in range(b)]
    else:
        marks = [x for x in range(1, b, 2)]
        expirations = [expirations[x] for x in marks]
    
    subplots = [x for x in range(1,idx - 1)]
    
    for subplot in subplots:
        eval("subplot{}.yaxis.set_ticks(marks)".format(subplot))
        eval("subplot{}.yaxis.set_ticklabels(expirations, fontsize = 10, verticalalignment= 'baseline', horizontalalignment= 'center')".format(subplot))
    
    mainTitle.insert(0, '{}: ${} @ [{} | {}]'.format(ticker, sharePrice, currentDate, currentTime))
    figure1.suptitle(''.join(mainTitle))
    figure1.set_facecolor(faceColor)
    matplotlib.pyplot.show(block=True)
    
             
def main():
    ticker, parameters, priceType, optionType, moneynessType, currentDate, currentTime = plotCheckandParams()
    StockOptions = returnOptions(currentDate, currentTime, ticker, optionType, priceType)
    plotOptions(StockOptions, parameters, ticker, currentDate, currentTime)
    
    
if __name__ == '__main__':
    # Main loop
    main()
           
