package haven.automation;

import java.awt.Color;
import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import haven.GameUI;

public class AutoKin implements Runnable {
	// private attribute pointing to GameUI
	private GameUI gui;
	
	// AutoKin constructor
	public AutoKin(GameUI gui) {
        this.gui = gui;
    }
	
	@Override
	public void run() {
		gui.syslog.append("AutoAdding Kin's:", Color.WHITE);
        Path file = Paths.get("secrets.txt");
        Charset charset = Charset.forName("UTF-8");
        try (BufferedReader reader = Files.newBufferedReader(file, charset)) {
            String line = null;
            while ((line = reader.readLine()) != null) {
                gui.syslog.append(line,Color.BLUE);
                gui.wdgmsg(gui.buddies,"bypwd",line);
            }
        } catch (IOException x) {
            gui.syslog.append("Exception: "+x.toString(),Color.RED);
        }
	}
}
