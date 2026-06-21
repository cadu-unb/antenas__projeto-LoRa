function antennas = loadAntennaModels()
%loadAntennaModels Base de dados dos modelos aproximados de antenas.

template = struct( ...
    'Name', '', ...
    'Type', '', ...
    'Gmax_dBi', NaN, ...
    'HPBW_deg', NaN, ...
    'Polarization', '', ...
    'IsDirectional', false, ...
    'PatternModel', '', ...
    'PracticalityScore', NaN, ...
    'MultiDirectionScore', NaN, ...
    'Notes', '');

antennas = repmat(template, 6, 1);

antennas(1).Name = 'Dipole_HalfWave';
antennas(1).Type = 'Omnidirectional vertical';
antennas(1).Gmax_dBi = 2.15;
antennas(1).HPBW_deg = 78;
antennas(1).Polarization = 'linear vertical';
antennas(1).IsDirectional = false;
antennas(1).PatternModel = 'dipole';
antennas(1).PracticalityScore = 8;
antennas(1).MultiDirectionScore = 9;
antennas(1).Notes = 'Omnidirecional no plano horizontal; nulos no eixo do dipolo; maximo perto de theta=90 graus.';

antennas(2).Name = 'Monopole_GroundPlane';
antennas(2).Type = 'Omnidirectional vertical';
antennas(2).Gmax_dBi = 5.15;
antennas(2).HPBW_deg = 55;
antennas(2).Polarization = 'linear vertical';
antennas(2).IsDirectional = false;
antennas(2).PatternModel = 'monopole';
antennas(2).PracticalityScore = 7;
antennas(2).MultiDirectionScore = 8;
antennas(2).Notes = 'Modelo ideal sobre plano de terra; energia concentrada perto do horizonte e no semiespaco superior.';

antennas(3).Name = 'Helical_Axial';
antennas(3).Type = 'Directional axial-mode helix';
antennas(3).Gmax_dBi = 11;
antennas(3).HPBW_deg = 55;
antennas(3).Polarization = 'circular/elliptical';
antennas(3).IsDirectional = true;
antennas(3).PatternModel = 'helical';
antennas(3).PracticalityScore = 5;
antennas(3).MultiDirectionScore = 3;
antennas(3).Notes = 'Direcional; ganho maximo no boresight; HPBW controla a largura aproximada do feixe.';

antennas(4).Name = 'Parabolic_Dish';
antennas(4).Type = 'Highly directional aperture';
antennas(4).Gmax_dBi = 20;
antennas(4).HPBW_deg = 18;
antennas(4).Polarization = 'linear or circular, feed-dependent';
antennas(4).IsDirectional = true;
antennas(4).PatternModel = 'parabolic';
antennas(4).PracticalityScore = 2;
antennas(4).MultiDirectionScore = 1;
antennas(4).Notes = ['Muito diretiva; inadequada para gateway unico recebendo muitos azimutes ', ...
    'sem multiplas antenas, setorizacao ou apontamento individual.'];

antennas(5).Name = 'PCB_Compact';
antennas(5).Type = 'Compact integrated antenna';
antennas(5).Gmax_dBi = 1;
antennas(5).HPBW_deg = 120;
antennas(5).Polarization = 'linear';
antennas(5).IsDirectional = false;
antennas(5).PatternModel = 'pcb';
antennas(5).PracticalityScore = 10;
antennas(5).MultiDirectionScore = 7;
antennas(5).Notes = 'Quase omnidirecional, baixo custo e compacta, com irregularidades simples em theta e phi.';

antennas(6).Name = 'Commercial_Omni_6dBi';
antennas(6).Type = 'Practical vertical omni';
antennas(6).Gmax_dBi = 6;
antennas(6).HPBW_deg = 35;
antennas(6).Polarization = 'linear vertical';
antennas(6).IsDirectional = false;
antennas(6).PatternModel = 'commercial_omni_6dbi';
antennas(6).PracticalityScore = 9;
antennas(6).MultiDirectionScore = 8;
antennas(6).Notes = 'Referencia pratica 868/915 MHz do kit E220: omnidirecional vertical, semelhante a monopolo/colinear.';
end

