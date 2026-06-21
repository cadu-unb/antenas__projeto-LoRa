============================================================
SIMULACAO LORA / ANTENAS - CAMPUS DARCY RIBEIRO UnB
============================================================

Gateway escolhido: BCE (modo: auto)

Ranking de candidatos a gateway:
         Name         MeanDistance_m    MaxDistance_m
    ______________    ______________    _____________

    {'BCE'       }        617.75           886.56    
    {'Beijodromo'}         578.8           907.06    
    {'IB'        }        545.61           1031.5    
    {'ICC Sul'   }        565.55           1066.6    
    {'SG'        }        682.64             1245    
    {'ICC Norte' }        687.12           1296.7    
    {'IQ'        }        704.69           1300.6    
    {'FACE'      }        963.92           1396.2    
    {'CO'        }        995.22           1396.2    

Coordenadas locais ENU, com origem no gateway:
         Name         East_m     North_m     Up_m 
    ______________    _______    _______    ______

    {'FACE'      }    -361.57     400.58    14.806
    {'BCE'       }          0          0         0
    {'Beijodromo'}     240.89    -277.42    4.5115
    {'IB'        }     94.399    -524.63    13.769
    {'IQ'        }     185.63     -779.3    18.318
    {'ICC Sul'   }     -242.5    -513.59    20.289
    {'ICC Norte' }    -473.81    -190.16    19.161
    {'CO'        }     812.17    -355.48    2.8255
    {'SG'        }    -406.05    -611.28    27.102

Geometria dos enlaces alarme -> gateway:
      PointName       Distance2D_m    Distance3D_m    AzimuthTxToGw_deg    ElevationTxToGw_deg    ThetaTxVertical_deg    ThetaRxVertical_deg
    ______________    ____________    ____________    _________________    ___________________    ___________________    ___________________

    {'FACE'      }       539.63          539.84            137.93                -1.5717                91.572                 88.428       
    {'Beijodromo'}       367.41          367.44            319.03               -0.70351                90.704                 89.296       
    {'IB'        }       533.05          533.23             349.8                -1.4796                 91.48                  88.52       
    {'IQ'        }       801.11          801.32             346.6                -1.3099                 91.31                  88.69       
    {'ICC Sul'   }       567.97          568.33            25.275                -2.0459                92.046                 87.954       
    {'ICC Norte' }       510.55          510.91            68.132                -2.1493                92.149                 87.851       
    {'CO'        }       886.56          886.56            293.64               -0.18261                90.183                 89.817       
    {'SG'        }       733.85          734.35            33.595                 -2.115                92.115                 87.885       


Amostra da tabela de calculo de enlace:
        Scenario           PointName          ModuleName             TxAntenna           GatewayAntenna       Distance2D_m    Distance3D_m    Azimuth_deg    Elevation_deg    Gtx_dBi    Grx_dBi    Ptx_dBm    Sensitivity_dBm    FSPL_dB    AdditionalLosses_dB    PolarizationLoss_dB    Prx_dBm    Margin_dB      LinkStatus       TxOrientation    GatewayOrientation
    _________________    ______________    _________________    ___________________    ___________________    ____________    ____________    ___________    _____________    _______    _______    _______    _______________    _______    ___________________    ___________________    _______    _________    _______________    _____________    __________________

    {'A_SameAntenna'}    {'FACE'      }    {'RFM95W_915MHz'}    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       539.63          539.84         137.93          -1.5717       2.1467     2.1467       20            -139          86.314             19                      0              -81.02      57.98      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'Beijodromo'}    {'RFM95W_915MHz'}    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       367.41          367.44         319.03         -0.70351       2.1493     2.1493       20            -139          82.972             19                      0             -77.673     61.327      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'IB'        }    {'RFM95W_915MHz'}    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       533.05          533.23          349.8          -1.4796       2.1471     2.1471       20            -139          86.207             19                      0             -80.912     58.088      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'IQ'        }    {'RFM95W_915MHz'}    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       801.11          801.32          346.6          -1.3099       2.1477     2.1477       20            -139          89.745             19                      0             -84.449     54.551      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'ICC Sul'   }    {'RFM95W_915MHz'}    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       567.97          568.33         25.275          -2.0459       2.1445     2.1445       20            -139           86.76             19                      0             -81.472     57.528      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'ICC Norte' }    {'RFM95W_915MHz'}    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       510.55          510.91         68.132          -2.1493       2.1439     2.1439       20            -139          85.835             19                      0             -80.547     58.453      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'CO'        }    {'RFM95W_915MHz'}    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       886.56          886.56         293.64         -0.18261         2.15       2.15       20            -139          90.623             19                      0             -85.323     53.677      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'SG'        }    {'RFM95W_915MHz'}    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       733.85          734.35         33.595           -2.115       2.1441     2.1441       20            -139          88.986             19                      0             -83.698     55.302      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'FACE'      }    {'LRO2_ASR6601' }    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       539.63          539.84         137.93          -1.5717       2.1467     2.1467       22            -138          86.314             19                      0              -79.02      58.98      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'Beijodromo'}    {'LRO2_ASR6601' }    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       367.41          367.44         319.03         -0.70351       2.1493     2.1493       22            -138          82.972             19                      0             -75.673     62.327      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'IB'        }    {'LRO2_ASR6601' }    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       533.05          533.23          349.8          -1.4796       2.1471     2.1471       22            -138          86.207             19                      0             -78.912     59.088      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'IQ'        }    {'LRO2_ASR6601' }    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       801.11          801.32          346.6          -1.3099       2.1477     2.1477       22            -138          89.745             19                      0             -82.449     55.551      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'ICC Sul'   }    {'LRO2_ASR6601' }    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       567.97          568.33         25.275          -2.0459       2.1445     2.1445       22            -138           86.76             19                      0             -79.472     58.528      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'ICC Norte' }    {'LRO2_ASR6601' }    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       510.55          510.91         68.132          -2.1493       2.1439     2.1439       22            -138          85.835             19                      0             -78.547     59.453      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'CO'        }    {'LRO2_ASR6601' }    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       886.56          886.56         293.64         -0.18261         2.15       2.15       22            -138          90.623             19                      0             -83.323     54.677      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'SG'        }    {'LRO2_ASR6601' }    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       733.85          734.35         33.595           -2.115       2.1441     2.1441       22            -138          88.986             19                      0             -81.698     56.302      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'FACE'      }    {'E220_900T22D' }    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       539.63          539.84         137.93          -1.5717       2.1467     2.1467       22            -137          86.314             19                      0              -79.02      57.98      {'Confortavel'}    {'vertical'}        {'vertical'}   
    {'A_SameAntenna'}    {'Beijodromo'}    {'E220_900T22D' }    {'Dipole_HalfWave'}    {'Dipole_HalfWave'}       367.41          367.44         319.03         -0.70351       2.1493     2.1493       22            -137          82.972             19                      0             -75.673     61.327      {'Confortavel'}    {'vertical'}        {'vertical'}   


Ranking de combinacoes modulo-antena:
             Scenario                ModuleName               TxAntenna                 GatewayAntenna         MinMargin_dB    MeanMargin_dB    Failures    CriticalLinks    ComfortableLinks    RobustnessScore    PracticalityScore    TxCurrent_mA    Score 
    __________________________    _________________    ________________________    ________________________    ____________    _____________    ________    _____________    ________________    _______________    _________________    ____________    ______

    {'C_DirectionalTxPointed'}    {'LRO2_ASR6601' }    {'Parabolic_Dish'      }    {'Commercial_Omni_6dBi'}       73.377          76.811           0              0                 8                  4.5                 11                NaN         108.13
    {'C_DirectionalTxPointed'}    {'E220_900T22D' }    {'Parabolic_Dish'      }    {'Commercial_Omni_6dBi'}       72.377          75.811           0              0                 8                  4.5                 11                NaN         106.88
    {'A_SameAntenna'         }    {'LRO2_ASR6601' }    {'Commercial_Omni_6dBi'}    {'Commercial_Omni_6dBi'}       62.377          65.803           0              0                 8                    8                 18                NaN         105.23
    {'B_OmniGateway_TxVaries'}    {'LRO2_ASR6601' }    {'Commercial_Omni_6dBi'}    {'Commercial_Omni_6dBi'}       62.377          65.803           0              0                 8                    8                 18                NaN         105.23
    {'E_ModuleComparison'    }    {'LRO2_ASR6601' }    {'Commercial_Omni_6dBi'}    {'Commercial_Omni_6dBi'}       62.377          65.803           0              0                 8                    8                 18                NaN         105.23
    {'A_SameAntenna'         }    {'E220_900T22D' }    {'Commercial_Omni_6dBi'}    {'Commercial_Omni_6dBi'}       61.377          64.803           0              0                 8                    8                 18                NaN         103.98
    {'B_OmniGateway_TxVaries'}    {'E220_900T22D' }    {'Commercial_Omni_6dBi'}    {'Commercial_Omni_6dBi'}       61.377          64.803           0              0                 8                    8                 18                NaN         103.98
    {'E_ModuleComparison'    }    {'E220_900T22D' }    {'Commercial_Omni_6dBi'}    {'Commercial_Omni_6dBi'}       61.377          64.803           0              0                 8                    8                 18                NaN         103.98
    {'C_DirectionalTxPointed'}    {'RFM95W_915MHz'}    {'Parabolic_Dish'      }    {'Commercial_Omni_6dBi'}       72.377          75.811           0              0                 8                  4.5                 11                120         103.28
    {'B_OmniGateway_TxVaries'}    {'LRO2_ASR6601' }    {'Commercial_Omni_6dBi'}    {'Monopole_GroundPlane'}       61.527          64.956           0              0                 8                    8                 16                NaN         102.57
    {'B_OmniGateway_TxVaries'}    {'LRO2_ASR6601' }    {'Monopole_GroundPlane'}    {'Commercial_Omni_6dBi'}       61.527           64.95           0              0                 8                    8                 16                NaN         102.56
    {'B_OmniGateway_TxVaries'}    {'E220_900T22D' }    {'Commercial_Omni_6dBi'}    {'Monopole_GroundPlane'}       60.527          63.956           0              0                 8                    8                 16                NaN         101.32
    {'B_OmniGateway_TxVaries'}    {'E220_900T22D' }    {'Monopole_GroundPlane'}    {'Commercial_Omni_6dBi'}       60.527           63.95           0              0                 8                    8                 16                NaN         101.31
    {'C_DirectionalTxPointed'}    {'LRO2_ASR6601' }    {'Helical_Axial'       }    {'Commercial_Omni_6dBi'}       64.377          67.811           0              0                 8                  5.5                 14                NaN         100.78
    {'A_SameAntenna'         }    {'RFM95W_915MHz'}    {'Commercial_Omni_6dBi'}    {'Commercial_Omni_6dBi'}       61.377          64.803           0              0                 8                    8                 18                120         100.38


Ranking por modulo LoRa:
       ModuleName        MinMargin_dB    MeanMargin_dB    Failures    CriticalLinks    ComfortableLinks    TxCurrent_mA    Score 
    _________________    ____________    _____________    ________    _____________    ________________    ____________    ______

    {'LRO2_ASR6601' }       27.03           58.072           0              0                280               NaN         41.548
    {'E220_900T22D' }       26.03           57.072           0              0                280               NaN         40.298
    {'RFM95W_915MHz'}       26.03           57.072           0              0                280               120         36.698


Ranking por antena transmissora:
           TxAntenna            MinMargin_dB    MeanMargin_dB    Failures    CriticalLinks    ComfortableLinks    TxCurrent_mA    Score 
    ________________________    ____________    _____________    ________    _____________    ________________    ____________    ______

    {'Commercial_Omni_6dBi'}       53.156          63.174           0              0                144               NaN         81.449
    {'Monopole_GroundPlane'}       52.306          61.759           0              0                120               NaN         79.246
    {'Dipole_HalfWave'     }       49.306          58.167           0              0                120               NaN         76.848
    {'PCB_Compact'         }       49.656          55.388           0              0                120               NaN         75.503
    {'Helical_Axial'       }        26.03          54.597           0              0                168               NaN          45.18
    {'Parabolic_Dish'      }       29.377          53.058           0              0                168               NaN         44.642


Ranking por antena do gateway:
         GatewayAntenna         MinMargin_dB    MeanMargin_dB    Failures    CriticalLinks    ComfortableLinks    TxCurrent_mA    Score 
    ________________________    ____________    _____________    ________    _____________    ________________    ____________    ______

    {'Commercial_Omni_6dBi'}       37.719          61.877           0              0                288               NaN         65.689
    {'Monopole_GroundPlane'}       36.873          59.596           0              0                168               NaN         63.272
    {'Dipole_HalfWave'     }       33.874          56.171           0              0                168               NaN         60.917
    {'PCB_Compact'         }       32.727          53.741           0              0                168               NaN         58.163
    {'Helical_Axial'       }        26.03          40.021           0              0                 24               NaN         41.535
    {'Parabolic_Dish'      }       29.377          40.097           0              0                 24               NaN         41.402


============================================================
DISCUSSAO AUTOMATICA
============================================================
Melhor antena para os nos transmissores pelo ranking agregado: Commercial_Omni_6dBi.
Melhor antena para o gateway pelo ranking agregado: Commercial_Omni_6dBi.
Modulo com melhor margem agregada: LRO2_ASR6601.

Estimativa simples de energia por transmissao (quando ha dados de corrente):
       ModuleName        Ptx_dBm    TxCurrent_mA    EnergyPerTx_J    DailyEnergy_J
    _________________    _______    ____________    _____________    _____________

    {'RFM95W_915MHz'}      20           120             0.33             7.92     
    {'LRO2_ASR6601' }      22           NaN              NaN              NaN     
    {'E220_900T22D' }      22           NaN              NaN              NaN     

Melhor modulo em consumo com dados disponiveis: RFM95W_915MHz.
Antenas muito diretivas, como helicoidal axial e parabolica, so entregam seu ganho maximo quando o boresight esta apontado para o gateway. Em um gateway unico recebendo de muitos azimutes, isso tende a reduzir a robustez, salvo com setorizacao, multiplas antenas ou apontamento controlado.
O cenario D isola esse efeito: transmissores diretivos desalinhados perdem margem porque Gtx(theta,phi) cai rapidamente fora do eixo de apontamento.

Variaveis principais no workspace: points, modules, antennas, geometry, results, rankings, energyTable.
>>