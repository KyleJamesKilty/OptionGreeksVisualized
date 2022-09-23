# OptionGreeksVisualized
### Introduction:
Graphs quantities representing the sensitivity of the price of options to a change in underlying parameters on which the value of an instrument or portfolio of financial instruments is dependent.

I've always believed that there is a better way to view what's going on behind stock options, rather than simply scrolling through lines and lines of option chains on Yahoo finance.

This project aims to visualize what is happening.

### Details:
The plotting is configurable by Mid-Price (Average of Recent Bids) or Last-price (Last recorded Bid).

Each function uses some or all of these parameters:  
    Stock price S \,  
    Strike price K \,  
    Risk-free rate r \,  
    Annual dividend yield q \,  
    Time to maturity {τ =T-t} (represented as a unit-less fraction of one year) ,  
    and Volatility σ .  

![Output of OptionGreeksVisualized](https://github.com/KyleJamesKilty/OptionGreeksVisualized/blob/Pictures/Option%20Greeks%20Pictures/Options.png?raw=true)

##### Examples of equations used
All equations taken from -> (https://en.wikipedia.org/wiki/Greeks_(finance))
![Output of OptionGreeksVisualized](https://github.com/KyleJamesKilty/OptionGreeksVisualized/blob/Pictures/Option%20Greeks%20Pictures/Greek_Outputs_Explanation.png?raw=true)

For more information on the parameters in these functions, please use the link to Greeks (finance) page above the picture.

## How to get this program running
1.Download Anaconda (https://www.anaconda.com/products/distribution)  
2.Open the Spyder development environment that comes installed with Anaconda.  
3.Install Yfinance package. Using "pip install yfinance" in console.  
4.Open the file or paste it into Spyder. Make sure it is saved with the .py extension.  
5.Press Run.  

This project was chosen for educational purposes for both programming and options.
