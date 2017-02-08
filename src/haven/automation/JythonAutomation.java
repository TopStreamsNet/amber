package haven.automation;

import org.python.util.PythonInterpreter;

import haven.HavenPanel;

import org.python.core.*;

public class JythonAutomation implements Runnable {
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
		System.out.println("--Running Jython Automation--");
		PythonInterpreter interp = new PythonInterpreter();
		interp.exec("import haven.MainFrame as MainFrame");
		interp.exec("print 123");
		System.out.println("--/Running Jython Automation--");
		

	}

	public void start() {
		// TODO Auto-generated method stub
		Thread jt = new Thread(JythonAutomation.getInstance(),"JBot thread");
		jt.start();
	}

}
