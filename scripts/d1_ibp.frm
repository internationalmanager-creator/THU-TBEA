* d1_ibp.frm
* Identidad IBP explicita para el sunset a 2-loops.
* Escribimos la derivada total a mano:
* d/dk1_mu [ k1_mu / (D1^n1 D2^n2 D3^n3) ] = 0

Symbols m, a, p, i, n1, n2, n3;
Vectors k1, k2, q;
Indices mu;

* Definir los propagadores
Local D1 = k1^2 * (1 + a*k1^2) - m^2;
Local D2 = k2^2 * (1 + a*k2^2) - m^2;
Local D3 = (k1+k2+q)^2 * (1 + a*(k1+k2+q)^2) - m^2;

* Derivada de D1 respecto a k1_mu (regla de la cadena)
* D1 = k1^2 + a*k1^4 - m^2
* dD1/dk1_mu = 2*k1(mu) + 4*a*k1^2*k1(mu) = 2*k1(mu)*(1 + 2*a*k1^2)
Local dD1 = 2*k1(mu)*(1 + 2*a*k1^2);

* Derivada de D2 respecto a k1_mu (D2 no depende de k1) = 0
Local dD2 = 0;

* Derivada de D3 respecto a k1_mu
* D3 = (k1+k2+q)^2 + a*(k1+k2+q)^4 - m^2
* dD3/dk1_mu = 2*(k1+k2+q)(mu) + 4*a*(k1+k2+q)^2*(k1+k2+q)(mu)
*            = 2*(k1+k2+q)(mu)*(1 + 2*a*(k1+k2+q)^2)
Local dD3 = 2*(k1(mu)+k2(mu)+q(mu))*(1 + 2*a*(k1+k2+q)^2);

* Identidad IBP: la derivada total es
* d/dk1_mu [ k1_mu / (D1^n1 D2^n2 D3^n3) ] 
* = (4 / (D1^n1 D2^n2 D3^n3)) 
*   - n1 * k1_mu * dD1 / (D1^(n1+1) D2^n2 D3^n3)
*   - n3 * k1_mu * dD3 / (D1^n1 D2^n2 D3^(n3+1))

Local IBP1 = 
    4 / (D1^n1 * D2^n2 * D3^n3)
  - n1 * k1(mu) * dD1 / (D1^(n1+1) * D2^n2 * D3^n3)
  - n3 * k1(mu) * dD3 / (D1^n1 * D2^n2 * D3^(n3+1));

* Simplificar
.sort

* Imprimir
Print IBP1;
.end
