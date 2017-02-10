package haven.automation;

import org.python.util.PythonInterpreter;

import haven.HavenPanel;

import org.python.core.*;

import java.awt.*;

public class JythonAutomation implements Runnable {
	private String botname = "";

	public static class JythonAutomationHolder {
		public static final JythonAutomation HOLDER_INSTANCE = new JythonAutomation();
	}
	public static JythonAutomation getInstance(){
		return JythonAutomationHolder.HOLDER_INSTANCE;
	}
		
	public JythonAutomation() {
		// TODO Auto-generated constructor stub
	}

	@Override
	public void run() {
		// TODO Auto-generated method stub
		HavenPanel.lui.cons.out.println("--Running Jython Automation: "+this.botname+"--");
		PythonInterpreter interp = new PythonInterpreter();
		interp.execfile(this.botname);
		HavenPanel.lui.cons.out.println("--/Running Jython Automation--");
		

	}

	public void start(String[] args) {
		HavenPanel.lui.cons.out.println("Args: "+args+" "+args[1]);
		this.botname = args[1];
		Thread jt = new Thread(JythonAutomation.getInstance(),"JBot thread");
		jt.start();
	}

}
