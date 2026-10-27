import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
public class DumpReview extends GhidraScript {
 public void run() throws Exception {
  try(PrintWriter w=new PrintWriter(new FileWriter(getScriptArgs()[0]))) {
   Function f=getFunctionContaining(toAddr("001c16d4"));
   InstructionIterator it=currentProgram.getListing().getInstructions(f.getBody(),true);
   while(it.hasNext()) {
    Instruction i=it.next(); w.println(i.getAddress()+" "+i.toString());
    for(Reference r:i.getReferencesFrom()) {
     if(r.getReferenceType().isCall()) w.println(" CALL "+r.getToAddress()+" "+getFunctionAt(r.getToAddress()));
    }
   }
   w.println("CALLERS OF MINADBD");
   for(Reference r:getReferencesTo(toAddr("001c61b0"))) w.println(r+" "+getFunctionContaining(r.getFromAddress()));
  }
 }
}
