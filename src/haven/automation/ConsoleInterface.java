package haven.automation;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import haven.HavenPanel;

public class ConsoleInterface implements Runnable {

	@Override
	public void run() {
		// TODO Auto-generated method stub
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		String cmd = null;
		while(true){
			System.out.print("?> ");
			try {
				cmd = br.readLine();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			System.out.println("< "+cmd);
			try {
				HavenPanel.lui.root.ui.cons.run(cmd);
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}

	}

}
