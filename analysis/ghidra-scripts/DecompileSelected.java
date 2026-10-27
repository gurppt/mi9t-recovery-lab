import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.io.*;
public class DecompileSelected extends GhidraScript {
 public void run() throws Exception {
  DecompInterface d=new DecompInterface(); d.openProgram(currentProgram);
  try(PrintWriter w=new PrintWriter(new FileWriter(getScriptArgs()[0]))) {
   for(int j=1;j<getScriptArgs().length;j++) {
    Function f=getFunctionContaining(toAddr(getScriptArgs()[j]));
    w.println("// "+f.getEntryPoint()+" "+f.getName());
    DecompileResults r=d.decompileFunction(f,60,monitor);
    if(r.decompileCompleted())w.println(r.getDecompiledFunction().getC()); else w.println(r.getErrorMessage());
   }
  }
  d.dispose();
 }
}
