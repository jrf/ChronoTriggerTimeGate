float h(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}
vec3 m(float t){
    t=clamp(t,0.,1.);
    return t<.25?mix(vec3(.02,.05,.2),vec3(.1,.2,.5),t/.25):t<.5?mix(vec3(.1,.2,.5),vec3(0.,.2,.8),(t-.25)/.25):t<.85?mix(vec3(0.,.2,.8),vec3(.3,.7,1.),(t-.5)/.35):t<.97?mix(vec3(.3,.7,1.),vec3(.7,.9,1.),(t-.85)/.12):vec3(.7,.9,1.);
}
void mainImage(out vec4 o,in vec2 f){
    vec2 r=iResolution.xy;
    float px=max(1.,floor(r.y/64.));
    vec2 u=(floor(f/px)*px+px*.5)/r,c=(u-.5)*2.;
    c.x*=r.x/r.y;
    float d=length(c);
    if(d>.92){o=vec4(0);return;}
    vec2 w=c;
    w.x+=.1*sin(w.y*2.);
    w.y+=.1*cos(w.x*2.);
    w+=.05*vec2(sin(w.y*5.),cos(w.x*5.));
    w+=.05*vec2(h(floor(w*30.)),h(floor(w*30.+10.)));
    vec2 q=u-vec2(.65);
    float s=length(q),a=atan(q.y,q.x)+5.*s;
    a+=.12*(h(floor(q*30.))-.5);
    s+=.02*(h(floor(q*30.+7.))-.5);
    w*=mix(.85,1.,smoothstep(0.,.35,s));
    float ph=3.*w.x+3.*w.y-1.8*exp(-2.*(w.y-w.x)*(w.y-w.x))-iTime*4.;
    float dp=fract(ph*.159+.5)-.5;
    float v=mix((pow(.5+.5*cos(ph),3.)*.8+.2*exp(-4.*dp*dp))*2.-1.,sin(5.*a+iTime*4.+2.*sin(5.*s)),smoothstep(.5,0.,s));
    o=vec4(m(v*.5+.5)*smoothstep(.92,.7,d),1.);
}
