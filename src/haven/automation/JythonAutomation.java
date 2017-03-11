package haven.automation;

import org.python.util.PythonInterpreter;

import haven.Config;
import haven.HavenPanel;

import java.io.File;
import java.io.FileInputStream;
import java.util.Properties;


public class JythonAutomation implements Runnable {
    private String botname = "";
    private Thread jt = null;

    public Thread getJt() {
        return jt;
    }

    public static class JythonAutomationHolder {
        public static final JythonAutomation HOLDER_INSTANCE = new JythonAutomation();
    }

    public static JythonAutomation getInstance() {
        return JythonAutomationHolder.HOLDER_INSTANCE;
    }

    public JythonAutomation() {
        // TODO Auto-generated constructor stub
    }

    @Override
    public void run() {
    	if(Config.headless)
        	System.out.println("--Running Jython Automation: " + this.botname + "--");
        HavenPanel.lui.cons.out.println("--Running Jython Automation: " + this.botname + "--");
        Properties props = new Properties();
        props.setProperty("python.path", System.getProperty("user.dir")+"/jbot/");
        PythonInterpreter.initialize(System.getProperties(), props, new String[] {""});
        PythonInterpreter interp = new PythonInterpreter();


        try {
            FileInputStream fis = new FileInputStream(new File("jbot/" + this.botname + ".py"));
            interp.execfile(fis);
        } catch (Exception e) {
            HavenPanel.lui.cons.out.println("Something went wrong!");
            e.printStackTrace(HavenPanel.lui.cons.out);
            if(Config.headless){
            	System.out.println("Something went wrong!");
            	e.printStackTrace(System.out);
            }
        }
        if(Config.headless)
        	System.out.println("--/Running Jython Automation--");
        HavenPanel.lui.cons.out.println("--/Running Jython Automation--");
    }

    public void start(String[] args) {
        this.botname = args[1];
        this.jt = new Thread(JythonAutomation.getInstance(), "JBot thread");
        this.jt.start();
    }

    public void headless(String[] args){
        if(args[1].equals("on")){
            Config.headless=true;
        }else{

        }
    }

}
