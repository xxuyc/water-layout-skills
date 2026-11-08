/** Native editable evidence symbols for an artifact-tool Slide. No inferred topology. */
export function createSymbols(slide, {fontFamily='Microsoft YaHei', colors={}}={}) {
  const palette = {black:'#171717', water:'#4578CE', valve:'#E83732', air:'#00D51B', added:'#2873B8', ...colors};
  let id=0;
  function shape(geometry,x,y,width,height,{fill='none',stroke=palette.black,lineWidth=1.6,name}={}) {
    return slide.shapes.add({name:name??`diagram-${++id}`,geometry,position:{left:x,top:y,width,height},fill,line:{fill:stroke,width:lineWidth,style:'solid'}});
  }
  function line(x1,y1,x2,y2,color=palette.black,width=1.6) {
    const x=Math.min(x1,x2),y=Math.min(y1,y2),w=Math.max(1,Math.abs(x2-x1)),h=Math.max(1,Math.abs(y2-y1));
    return slide.shapes.add({name:`line-${++id}`,geometry:'custom',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:color,width,style:'solid'},customPaths:[{width:w,height:h,commands:[{moveTo:{x:x1-x,y:y1-y}},{lineTo:{x:x2-x,y:y2-y}}]}]});
  }
  function pipe(points,color=palette.water,width=3) {
    return points.slice(1).map((p,i)=>line(...points[i],...p,color,width));
  }
  function text(value,x,y,{width,height,size=22,align='left',color=palette.black,bold=false,name}={}) {
    if (!(width>0 && height>0)) throw new Error('Pass explicit measured width and height');
    const left=align==='center'?x-width/2:align==='right'?x-width:x;
    const result=shape('textbox',left,y,width,height,{stroke:'none',lineWidth:0,name});
    result.text=value;
    result.text.style={typeface:fontFamily,fontSize:size,color,alignment:align,bold};
    result.text.insets={left:2,right:2,top:0,bottom:0};
    return result;
  }
  function arrow(x,y,direction='r',length=34,color=palette.water) {
    const g={r:'rightArrow',l:'leftArrow',u:'upArrow',d:'downArrow'}[direction];
    if(!g) throw new Error('Direction must be r, l, u or d');
    const vertical=direction==='u'||direction==='d';
    return shape(g,x,y,vertical?10:length,vertical?length:10,{fill:color,stroke:'none',lineWidth:0});
  }
  function instrument(x,y,r=12) {
    return [shape('ellipse',x-r,y-r,2*r,2*r,{fill:'white'}),line(x-r*.67,y-r*.67,x+r*.67,y+r*.67),line(x-r*.67,y+r*.67,x+r*.67,y-r*.67)];
  }
  function pump(x,y,r=14) {
    return [shape('ellipse',x-r,y-r,2*r,2*r,{fill:'white'}),shape('triangle',x-r*.57,y-r*.57,1.14*r,1.14*r,{fill:palette.black,stroke:palette.black,lineWidth:0})];
  }
  function valve(x,y,{electric=false,color=palette.valve,r=11}={}) {
    const result=[shape('ellipse',x-r,y-r,2*r,2*r,{fill:'white',stroke:color}),line(x-r*.73,y-r*.64,x+r*.73,y+r*.64,color),line(x-r*.73,y+r*.64,x+r*.73,y-r*.64,color)];
    if(electric) result.push(line(x,y-r,x,y-r-10,color),shape('rect',x-5,y-r-17,10,7,{fill:'white',stroke:color}));
    return result;
  }
  function flow(x,y,{color=palette.black,r=14}={}) {
    const circle=shape('ellipse',x-r,y-r,2*r,2*r,{fill:'white',stroke:color});
    const label=text('F',x,y-r-1,{width:2*r,height:2*r+3,size:21,align:'center',color});
    return [circle,label];
  }
  return {palette,shape,line,pipe,text,arrow,instrument,pump,valve,flow};
}
