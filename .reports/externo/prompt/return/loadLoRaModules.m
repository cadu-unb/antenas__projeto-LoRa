function modules = loadLoRaModules(defaultSensitivity_dBm)
%loadLoRaModules Base de dados dos modulos LoRa usados na comparacao.
%   modules = loadLoRaModules() deixa a sensibilidade do E220 como NaN.
%   modules = loadLoRaModules(defaultSensitivity_dBm) usa esse valor como
%   hipotese ajustavel para simulacoes automaticas do E220-900T22D.

if nargin < 1
    defaultSensitivity_dBm = NaN;
end

template = struct( ...
    'Name', '', ...
    'f_MHz', 915, ...
    'PtxMin_dBm', NaN, ...
    'PtxMax_dBm', NaN, ...
    'PtxOptions_dBm', [], ...
    'SensitivityOptions_dBm', [], ...
    'VoltageMin_V', NaN, ...
    'VoltageMax_V', NaN, ...
    'RxCurrent_mA', [], ...
    'TxCurrentOptions_mA', [], ...
    'SleepCurrent_uA', NaN, ...
    'IdleCurrent_uA', NaN, ...
    'DataRateMin_kbps', NaN, ...
    'DataRateMax_kbps', NaN, ...
    'Interface', '', ...
    'Modulation', 'LoRa', ...
    'Notes', '');

modules = repmat(template, 3, 1);

modules(1).Name = 'RFM95W_915MHz';
modules(1).f_MHz = 915;
modules(1).PtxMin_dBm = 13;
modules(1).PtxMax_dBm = 20;
modules(1).PtxOptions_dBm = [13 17 20];
modules(1).TxCurrentOptions_mA = [13 29; 17 90; 20 120];
modules(1).SensitivityOptions_dBm = [-139 -136 -118];
modules(1).VoltageMin_V = 1.8;
modules(1).VoltageMax_V = 3.7;
modules(1).RxCurrent_mA = [10 14];
modules(1).SleepCurrent_uA = 0.2;
modules(1).IdleCurrent_uA = 1.5;
modules(1).DataRateMin_kbps = 0.018;
modules(1).DataRateMax_kbps = 37.5;
modules(1).Interface = 'SPI';
modules(1).Notes = ['Sensibilidades tratadas como modos: LongRange=-139 dBm, ', ...
    'Balanced=-136 dBm, HighDataRate=-118 dBm. Erro de frequencia +/-7 kHz; FIFO 64 bytes; ', ...
    'temperatura -40 C a 85 C.'];

modules(2).Name = 'LRO2_ASR6601';
modules(2).f_MHz = 915;
modules(2).PtxMin_dBm = 0;
modules(2).PtxMax_dBm = 22;
modules(2).PtxOptions_dBm = [0 10 14 17 20 22];
modules(2).TxCurrentOptions_mA = [NaN NaN];
modules(2).SensitivityOptions_dBm = -138;
modules(2).VoltageMin_V = 3.0;
modules(2).VoltageMax_V = 5.5;
modules(2).RxCurrent_mA = NaN;
modules(2).DataRateMin_kbps = NaN;
modules(2).DataRateMax_kbps = NaN;
modules(2).Interface = 'Nao informado';
modules(2).Notes = ['Suporta 433, 475, 868 e 915 MHz; simulacao em 915 MHz. ', ...
    'Modulo 36 mm x 16.5 mm; referencia ate 8 km em visada aberta e ate 3.8 km urbano.'];

modules(3).Name = 'E220_900T22D';
modules(3).f_MHz = 915;
modules(3).PtxMin_dBm = 10;
modules(3).PtxMax_dBm = 22;
modules(3).PtxOptions_dBm = [10 14 17 20 22];
modules(3).TxCurrentOptions_mA = [NaN NaN];
modules(3).SensitivityOptions_dBm = defaultSensitivity_dBm;
modules(3).VoltageMin_V = NaN;
modules(3).VoltageMax_V = NaN;
modules(3).RxCurrent_mA = NaN;
modules(3).Interface = 'UART/configuravel';
modules(3).Notes = ['Faixa 815.125 a 930.125 MHz; simulacao em 915 MHz. ', ...
    'Sensibilidade nao informada nos dados fornecidos: campo usa NaN por padrao ou hipotese ajustavel. ', ...
    'Potencia registrada como 10 a 22 dBm, apesar da inconsistencia comercial entre 100 mW e 22 dBm. ', ...
    'Kit acompanha antenas SMA-J 868/915 MHz, 6 dBi, omnidirecionais, polarizacao vertical, cabo de 1 m.'];
end

