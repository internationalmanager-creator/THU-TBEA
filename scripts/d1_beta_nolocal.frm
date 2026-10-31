* d1_beta_nolocal.frm
* Calculo de la funcion beta a 1-loop para el campo tau con
* operador no local expandido a primer orden: exp(a*k^2) ~ 1 + a*k^2.
* Verificamos si el operador no local cambia la estructura de la funcion beta.

Symbols g, m, p, i, a;
Vectors k, p1, p2;
Indices mu, nu;

* Propagador no local expandido a orden a
Local Prop = i / (k^2 * (1 + a*k^2) - m^2);

* Vertice de interaccion
Local Vert = -i * g;

* Integral de 1-loop (tadpole)
Local Tadpole = Vert * Prop;

* Integral de 1-loop (bubble)
Local Bubble = Vert^2 * Prop * Prop;

.sort

Print Tadpole, Bubble;
.end
