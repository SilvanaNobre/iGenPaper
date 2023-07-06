"""
Created on May 09th 2022
@author: Silvana R Nobre
"""
import math

def PennsylvaniaYield(Age, SiteLst, ForestTypeLst, EcoRegionLst, Stock, Intervention, YieldType) -> float:
    # Gilabert, H., Manning, P.J., McDill, M.E., Sterner, S., 2010.
    #    Sawtimber yield tables for Pennsylvania forest management planning.
    #    North. J. Appl. For. 27, 140–150. https://doi.org/10.1093/njaf/27.4.140

    # Function to calculate Total Net sawtimber volume
    # coefficients
    #--------------------------------------------------
    # Intercepter; Age coefficient
    alfa = {0:9.65161,1:-79.67558}
    # Sites coefficients
    beta = {1:0.48990, 2:0, 3:-0.90516}
    # Forest Types coefficients
    phi = {1:0.23674, 2:0.55308, 3:0.05102, 4:0.31938, 5:0, 6:-0.04277, 7:0.46172}
    # Ecological Regions coefficients
    gamma = {1:-0.19182, 2:0, 3:0, 4:0, 5:0.37972, 6:0, 7:0, 8:0.40850, 9:0, 10:0, 11:0, 12:0, 13:0}
    # Stock coefficients
    lda = {'stocked':0, 'understocked':-0.41902}

    x_alfa = alfa[0]
    if Age > 0:
       x_alfa += alfa[1]/Age
    x_beta = 0
    for iSite in SiteLst:
        x_beta += beta[iSite]
    x_phi = 0
    for iFType in ForestTypeLst:
        x_phi += phi[iFType]
    x_gamma = 0
    for iERegion in EcoRegionLst:
        x_gamma += gamma[iERegion]
    x_lambda = lda[Stock]

    x = x_alfa + x_beta + x_phi + x_gamma + x_lambda
    x = math.exp(x)

    if Intervention == 'SWC':
        if YieldType == 'Removed':
            Rate = 0.4
        elif YieldType == 'Remaining':
            Rate = 0.6
        elif YieldType == 'Standing':
            Rate = 1
    elif Intervention == 'OR':
        if YieldType == 'Removed':
            Rate = 0.6
        elif YieldType == 'Remaining':
            Rate = 0
        elif YieldType == 'Standing':
            Rate = 0.6
    elif Intervention == 'OR1':
        if YieldType == 'Removed':
            Rate = 1
        elif YieldType == 'Remaining':
            Rate = 0
        elif YieldType == 'Standing':
            Rate = 1
    elif Intervention == 'ni':
        if YieldType == 'Removed':
            Rate = 0
        elif YieldType == 'Remaining':
            Rate = 0
        elif YieldType == 'Standing':
            Rate = 1
    x = Rate * x
    return x

def fcGrowth(Age, SiteIndex, Stratum, TPH, BasalArea, TVolume, RetVariable) -> float:
    #:Age,:SiteIndex, :Stratum, :TPH, :BasalArea, 'BasalArea'
    # Mato Grosso(Stratum 1)  Para (Stratum 2)

    if Stratum == 1 :
       baP_a = 1.7684
       baP_b = 0.09381
       tvP_a = 1.29779
       tvP_b = -2.10115
       tvP_c = 1.090832
       tvP_d = 0.030099
    else:
       baP_a = 2.682099
       baP_b = 0.067715
       tvP_a = 1.332057
       tvP_b = -2.51478
       tvP_c = 1.078489
       tvP_d = 0.030271

    if BasalArea == 0 and (Age+1) < 3:
        ReturnValue = 0
    else:
      if BasalArea == 0 and (Age+1) >= 3:
         BasalArea = 8
         BasalAreaProj = 11
      else:
         BasalAreaProj = math.exp( math.log(BasalArea) * Age/(Age+1) + baP_a * (1 - (Age/(Age+1))) + baP_b * (1 - (Age/(Age+1))) * SiteIndex )

      if RetVariable == 'BasalArea' :
           ReturnValue =  BasalAreaProj
      else:
           DBHProj = math.sqrt(BasalAreaProj * 40000 / (TPH * math.pi))
           if RetVariable == 'DBH':
              ReturnValue = DBHProj
           else:
              if Age == 0:
                  TVolumeProj = 0
              else:
                  x1 = math.exp(tvP_a + tvP_b * (1/(Age+1)) + tvP_c * math.log(BasalAreaProj) + tvP_d * SiteIndex)
                  x2 = math.exp(tvP_a + tvP_b * (1/Age) + tvP_c * math.log(BasalArea) + tvP_d * SiteIndex)
                  TVolumeProj = TVolume * x1 / x2
              if RetVariable == 'TVolume':
                 ReturnValue = TVolumeProj
              else:
                 CVolumeProj = TVolumeProj * math.exp(-6 / DBHProj)
                 if RetVariable == 'CVolume':
                    ReturnValue = CVolumeProj
                 else:
                    ReturnValue = -1

    return ReturnValue

def fcIntervention(TPH, BasalArea, AiTPH, TVolume, CVolume, RetVariable) -> float:

    PercTPH = (TPH - AiTPH) / TPH
    PercBasalArea = PercTPH ** 1.15

    RvBasalArea = BasalArea * PercBasalArea
    AiBasalArea = BasalArea - RvBasalArea

    if RetVariable == 'RvBasalArea':
       ReturnValue =  RvBasalArea
    elif RetVariable == 'AiBasalArea':
         ReturnValue = AiBasalArea
    else:
         RvTPH = TPH - AiTPH
         if RetVariable == 'RvTPH':
            ReturnValue = RvTPH
         else:
             RvTVolume = TVolume * PercBasalArea
             AiTVolume = TVolume - RvTVolume
             if RetVariable == 'RvTVolume':
                ReturnValue = RvTVolume
             elif RetVariable == 'AiTVolume':
                 ReturnValue = AiTVolume
             else:
                 RvCVolume = CVolume * PercBasalArea
                 AiCVolume = CVolume - RvCVolume
                 if RetVariable == 'RvCVolume':
                     ReturnValue = RvCVolume
                 elif RetVariable == 'AiCVolume':
                     ReturnValue = AiCVolume
                 else:
                     RvDBH = math.sqrt(RvBasalArea * 40000.00 / (RvTPH * math.pi) )
                     if AiTPH == 0:
                        AiDBH = 0
                     else:
                        AiDBH = math.sqrt(AiBasalArea * 40000.00 / (AiTPH * math.pi) )
                     if RetVariable == 'RvDBH':
                         ReturnValue = RvDBH
                     elif RetVariable == 'AiDBH':
                         ReturnValue = AiDBH
                     else:
                         ReturnValue = -1
    return ReturnValue

if __name__ == '__main__':
    Age = 13.16
    SiteIndex = 22.81
    Stratum = 1
    TPH = 149
    BasalArea = 10.51
    TVolume = 98.10
    CVolume = 80
    AiTPH = 100

    RetVariable = 'AiBasalArea'
    RetVar = fcIntervention(TPH, BasalArea, AiTPH, TVolume, CVolume, RetVariable)
    print('AiBasalArea '+ str(RetVar))
    RetVariable = 'AiDBH'
    RetVar = fcIntervention(TPH, BasalArea, AiTPH, TVolume, CVolume, RetVariable)
    print('AiDBH '+ str(RetVar))
    RetVariable = 'AiTVolume'
    RetVar = fcIntervention(TPH, BasalArea, AiTPH, TVolume, CVolume, RetVariable)
    print('AiTVolume ' + str(RetVar))
    RetVariable = 'AiCVolume'
    RetVar = fcIntervention(TPH, BasalArea, AiTPH, TVolume, CVolume, RetVariable)
    print('AiCVolume '+ str(RetVar))
    RetVariable = 'RvBasalArea'
    RetVar = fcIntervention(TPH, BasalArea, AiTPH, TVolume, CVolume, RetVariable)
    print('RvBasalArea ' + str(RetVar))
    RetVariable = 'RvTPH'
    RetVar = fcIntervention(TPH, BasalArea, AiTPH, TVolume, CVolume, RetVariable)
    print('RvTPH '+ str(RetVar))
    RetVariable = 'RvDBH'
    RetVar = fcIntervention(TPH, BasalArea, AiTPH, TVolume, CVolume, RetVariable)
    print('RvDBH ' + str(RetVar))
    RetVariable = 'RvTVolume'
    RetVar = fcIntervention(TPH, BasalArea, AiTPH, TVolume, CVolume, RetVariable)
    print('RvTVolume ' + str(RetVar))
    RetVariable = 'RvCVolume'
    RetVar = fcIntervention(TPH, BasalArea, AiTPH, TVolume, CVolume, RetVariable)
    print( 'RvCVolume ' + str(RetVar))






