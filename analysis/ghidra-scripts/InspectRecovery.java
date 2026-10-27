import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.address.*;
import java.io.*;
import java.util.*;

public class InspectRecovery extends GhidraScript {
 public void run() throws Exception {
  String out=getScriptArgs()[0];
  Set<Function> targets=new LinkedHashSet<>();
  try(PrintWriter w=new PrintWriter(new FileWriter(out))) {
   FunctionIterator fi=currentProgram.getFunctionManager().getFunctions(true);
   while(fi.hasNext()) {
    Function f=fi.next(); String n=f.getName();
    if(n.contains("service_to_")||n.contains("file_sync")||n.contains("handle_send")||n.contains("handle_recv")||n.contains("do_send")||n.contains("do_recv")||n.contains("send_impl")||n.contains("recv_impl")||n.contains("secure_mkdir")||n.contains("minadbd_main")||n.contains("handle_packet")||n.toLowerCase().contains("frp")||n.toLowerCase().contains("mitoken")) targets.add(f);
   }
   DataIterator di=currentProgram.getListing().getDefinedData(true);
   while(di.hasNext()) {
    Data d=di.next(); Object value=d.getValue();
    if(!(value instanceof String)) continue;
    String s=(String)value;
    if(s.contains("format-frp")||s.contains("getmitoken")||s.contains("failed_decrypt")||s.contains("failed_mitoken")||s.equals("sync:")||s.contains("/dev/block/by-name/frp")) {
     w.println("STRING "+d.getAddress()+" "+s);
     ReferenceIterator ri=currentProgram.getReferenceManager().getReferencesTo(d.getAddress());
     while(ri.hasNext()) { Reference r=ri.next(); Function f=currentProgram.getFunctionManager().getFunctionContaining(r.getFromAddress()); w.println(" XREF "+r.getFromAddress()+" "+f); if(f!=null)targets.add(f); }
    }
   }
   for(String needle: new String[]{"failed_decrypt_error","failed_mitoken_is_NULL","/dev/block/by-name/frp","format-frp:"}) {
    Address a=currentProgram.getMinAddress();
    while(a!=null) {
     a=currentProgram.getMemory().findBytes(a,needle.getBytes("UTF-8"),null,true,monitor);
     if(a==null)break;
     w.println("RAWSTRING "+a+" "+needle);
     ReferenceIterator ri=currentProgram.getReferenceManager().getReferencesTo(a);
     while(ri.hasNext()) { Reference r=ri.next(); Function f=currentProgram.getFunctionManager().getFunctionContaining(r.getFromAddress()); w.println(" XREF "+r.getFromAddress()+" "+f); if(f!=null)targets.add(f); }
     a=a.next();
    }
   }
   for(int j=1;j<getScriptArgs().length;j++) {
    Function f=currentProgram.getFunctionManager().getFunctionContaining(toAddr(getScriptArgs()[j]));
    if(f!=null)targets.add(f);
   }
   DecompInterface dec=new DecompInterface(); dec.openProgram(currentProgram);
   for(Function f:targets) {
    w.println("\n// FUNCTION "+f.getEntryPoint()+" "+f.getName());
    DecompileResults r=dec.decompileFunction(f,60,monitor);
    if(r.decompileCompleted())w.println(r.getDecompiledFunction().getC()); else w.println(r.getErrorMessage());
    w.flush();
   }
   dec.dispose();
  }
 }
}
