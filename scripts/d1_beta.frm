* d1_beta.frm
* Calculo de la funcion beta a 1-loop para una teoria escalar phi^4.

Symbols g, m, p, i;
Vectors k, p1, p2;
Indices mu, nu;

Local Prop = 1 / (k^2 - m^2);
Local Vert = -i * g;

Local Tadpole = Vert * Prop;
Local Bubble = Vert^2 * Prop * Prop;

.sort

Print Tadpole, Bubble;
.end
