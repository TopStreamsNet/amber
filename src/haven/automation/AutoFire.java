package haven.automation;

import static haven.OCache.posres;

import java.awt.Color;
import java.awt.Font;
import java.awt.event.KeyEvent;
import java.util.ArrayList;
import java.util.List;

import haven.*;

public class AutoFire extends Window implements GobSelectCallback {
	private static final Text.Foundry infof = new Text.Foundry(Text.sans, 10).aa(true);
	private static final Text.Foundry countf = new Text.Foundry(Text.sans.deriveFont(Font.BOLD), 12).aa(true);
	private List<Gob> fires = new ArrayList<>();
	private List<Gob> stockpiles = new ArrayList<>();
	private final Label lblf, lbls;
	public boolean terminate = false;
	private Button clearbtn, runbtn, stopbtn;
	private static final int TIMEOUT = 2000;
	private static final int HAND_DELAY = 8;
	private static final int SLEEP = 30 * 60 * 1000; // 30 min
	private Thread runner;

	public AutoFire() {
		super(new Coord(270, 180), "Auto Fire");

		final Label lbl = new Label("Alt + Click to select fireplaces and stockpiles.", infof);
		add(lbl, new Coord(30, 20));

		Label lblctxt = new Label("Fires Selected:", infof);
		add(lblctxt, new Coord(15, 60));
		lblf = new Label("0", countf, true);
		add(lblf, new Coord(110, 58));

		Label lblstxt = new Label("Stockpiles Selected:", infof);
		add(lblstxt, new Coord(135, 60));
		lbls = new Label("0", countf, true);
		add(lbls, new Coord(235, 58));

		clearbtn = new Button(140, "Clear Selection") {
			@Override
			public void click() {
				fires.clear();
				stockpiles.clear();
				lblf.settext(fires.size() + "");
				lbls.settext(stockpiles.size() + "");
			}
		};
		add(clearbtn, new Coord(65, 90));

		runbtn = new Button(140, "Run") {
			@Override
			public void click() {
				if (fires.size() == 0) {
					gameui().error("No fires selected.");
					return;
				} else if (stockpiles.size() == 0) {
					gameui().error("No stockpiles selected.");
					return;
				}

				this.hide();
				cbtn.hide();
				clearbtn.hide();
				stopbtn.show();
				terminate = false;

				runner = new Thread(new Runner(), "Auto Fire");
				runner.start();
			}
		};
		add(runbtn, new Coord(65, 140));

		stopbtn = new Button(140, "Stop") {
			@Override
			public void click() {
				terminate = true;
				// TODO: terminate PF
				this.hide();
				runbtn.show();
				clearbtn.show();
				cbtn.show();
			}
		};
		stopbtn.hide();
		add(stopbtn, new Coord(65, 140));
	}

	private class Runner implements Runnable {

		@Override
		public void run() {
			GameUI gui = gameui();
			while (!terminate) {
				gui.syslog.append("Starting Loop!",Color.CYAN);
				floop: for (Gob f : fires) {
					// take fuel from stockpiles if we don't have enough in the
					// inventory
					int availableFuelBlock = gui.maininv.getItemPartialCount("Block");
					if (availableFuelBlock < 3)
						getfuel();

					// find one piece of fuel in the inventory
					WItem fuel = gui.maininv.getItemPartial("Block");
					if (fuel == null)
						continue;

					int fuelticks = 50; // it takes two blocks to fill the fire to 100

					// navigate to fire
					gui.map.pfRightClick(f, -1, 3, 0, null);
					try {
						gui.map.pfthread.join();
					} catch (InterruptedException e) {
						return;
					}

					if (terminate)
						return;
					
					try {
                        Thread.sleep(TIMEOUT);
                    } catch (InterruptedException e) {
                        return;
                    }
					
					Window cwnd = gui.getwnd("Fireplace");
					if (cwnd == null)
						continue;
					VMeter vm = cwnd.getchild(VMeter.class);
					if (vm == null)
						continue;

					gui.syslog.append("VMeter: "+vm.amount+" > "+(100-fuelticks),Color.CYAN);
					if (vm.amount > (100 - fuelticks))
						continue;

					int fueltoload = (100 - vm.amount) / fuelticks;
					
					// take fuel
					fuel.item.wdgmsg("take", new Coord(fuel.item.sz.x / 2, fuel.item.sz.y / 2));
					int timeout = 0;
					while (gui.hand.isEmpty()) {
						timeout += HAND_DELAY;
						if (timeout >= TIMEOUT)
							continue floop;
						try {
							Thread.sleep(HAND_DELAY);
						} catch (InterruptedException e) {
							return;
						}
					}
					gui.syslog.append("Hand is not empty!", Color.CYAN);
					for (; fueltoload > 0; fueltoload--) {
						if (terminate)
							return;
						while(!gui.hand.isEmpty()){
						gui.map.wdgmsg("itemact", Coord.z, f.rc.floor(posres), fueltoload == 1 ? 0 : 1, 0, (int) f.id,
								f.rc.floor(posres), 0, -1);
						try {
							Thread.sleep(1000);
						} catch (InterruptedException e) {
							return;
						}
						}
						timeout = 0;
						while (true) {
							WItem newfuel = gui.vhand;
							if (newfuel != fuel) {
								fuel = newfuel;
								break;
							}

							timeout += HAND_DELAY;
							if (timeout >= TIMEOUT)
								break;
							try {
								Thread.sleep(HAND_DELAY);
							} catch (InterruptedException e) {
								return;
							}
						}
					}

					WItem hand = gui.vhand;
					// if the fireplace is full already we'll end up with a
					// stockpile on the cursor
					if (hand != null) {
						gui.map.wdgmsg("place", Coord.z, 0, 3, 0);
						gui.map.wdgmsg("drop", hand.c.add(Inventory.sqsz.div(2)).div(Inventory.invsq.sz()));
					}
				}

			try {
				Thread.sleep(SLEEP);
			} catch (InterruptedException e) {
				return;
			}

			}

		}
	}

	private void getfuel() {
		GameUI gui = gameui();
		Glob glob = gui.map.glob;
		for (Gob s : stockpiles) {
			if (terminate)
				return;

			// make sure stockpile still exists
			synchronized (glob.oc) {
				if (glob.oc.getgob(s.id) == null)
					continue;
			}

			// navigate to the stockpile and load up on fuel
			gameui().map.pfRightClick(s, -1, 3, 1, null);
			try {
				gui.map.pfthread.join();
			} catch (InterruptedException e) {
				return;
			}

			// return if got enough fuel
			int availableFuelBlock = gui.maininv.getItemPartialCount("Block");
			if (availableFuelBlock >= 3)
				return;
		}
	}

	@Override
	public void gobselect(Gob gob) {
		Resource res = gob.getres();
		if (res != null) {
			if (res.name.equals("gfx/terobjs/pow")) {
				if (!fires.contains(gob)) {
					fires.add(gob);
					lblf.settext(fires.size() + "");
				}
			} else if (res.name.equals("gfx/terobjs/stockpile-wblock")) {
				if (!stockpiles.contains(gob)) {
					stockpiles.add(gob);
					lbls.settext(stockpiles.size() + "");
				}
			}
		}
	}

	@Override
	public void wdgmsg(Widget sender, String msg, Object... args) {
		if (sender == cbtn)
			reqdestroy();
		else
			super.wdgmsg(sender, msg, args);
	}

	@Override
	public boolean type(char key, KeyEvent ev) {
		if (key == 27) {
			if (cbtn.visible)
				reqdestroy();
			return true;
		}
		return super.type(key, ev);
	}

	public void terminate() {
		terminate = true;
		if (runner != null)
			runner.interrupt();
		this.destroy();
	}

}
