* d1_expandir_a.frm - expansion en a del sunset no local
Symbols m, a, p;
Vectors k1, k2, q;

Local Jloc = 1/((k1^2-m^2)*(k2^2-m^2)*((k1+k2+q)^2-m^2));

Local I1 = 
  - a*k1^4/((k1^2-m^2)^2*(k2^2-m^2)*((k1+k2+q)^2-m^2))
  - a*k2^4/((k1^2-m^2)*(k2^2-m^2)^2*((k1+k2+q)^2-m^2))
  - a*(k1+k2+q)^4/((k1^2-m^2)*(k2^2-m^2)*((k1+k2+q)^2-m^2)^2);

.sort
Print Jloc;
Print I1;
.end
