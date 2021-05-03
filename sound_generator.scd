c = 0;
q = 330;
a = 0.5;
l = 0;


s.boot;
(
//open FuncStream
p = "sc-input.txt";
f = File(p,"r");
x = FileReader(f, true, false, "\n").postcs;
x = x.collect(_.collect(_.interpret));
)
// Adapted from https://composerprogrammer.com/teaching/supercollider/sctutorial/3.3%20Sequencing.html
(
SynthDef(\event,{ arg freq=440, amp=0.5, pan=0.0;

	var env;
	env = EnvGen.ar(  Env([0,1,1,0],[0.01, 0.1, 0.2]),  doneAction:2);

	Out.ar(0, SinOsc.ar(freq, 0.0, 0.3) * env * amp);

}).add;
)

(
{
	x.reset;
	5000.do {
		q = x.next;
		a = x.next;
		l = x.next;
		q.post; a.post; l.postln;
		Synth(\event,[\freq,q,\amp,a]);
		0.20.wait;
	};
}.fork;
)


