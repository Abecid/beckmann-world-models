"use strict";
const videos=[...document.querySelectorAll("video")];
const button=document.getElementById("play-examples");
function update(){const playing=videos.some(v=>!v.paused);button.textContent=playing?"Pause examples":"Play examples";button.setAttribute("aria-pressed",String(playing));}
button.addEventListener("click",async()=>{if(videos.some(v=>!v.paused))videos.forEach(v=>v.pause());else{videos.forEach(v=>v.currentTime=0);await Promise.allSettled(videos.map(v=>v.play()));}update();});
videos.forEach(v=>{v.addEventListener("play",update);v.addEventListener("pause",update);});
function pause(){videos.forEach(v=>v.pause());update();}
document.addEventListener("visibilitychange",()=>{if(document.hidden)pause();});
window.matchMedia("(prefers-reduced-motion: reduce)").addEventListener("change",e=>{if(e.matches)pause();});
