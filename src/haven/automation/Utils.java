package haven.automation;

import haven.*;

import java.util.Formatter;


public class Utils {
    private static final int HAND_DELAY = 5;
    private static final int PROG_ACT_DELAY = 8;
    private static final int PROG_FINISH_DELAY = 70;

    public static boolean waitForEmptyHand(GameUI gui, int timeout, String error) throws InterruptedException {
        int t = 0;
        while (gui.vhand != null) {
            t += HAND_DELAY;
            if (t >= timeout) {
                gui.error(error);
                return false;
            }
            try {
                Thread.sleep(HAND_DELAY);
            } catch (InterruptedException ie) {
                throw ie;
            }
        }
        return true;
    }

    public static boolean waitForOccupiedHand(GameUI gui, int timeout, String error) throws InterruptedException {
        int t = 0;
        while (gui.vhand == null) {
            t += HAND_DELAY;
            if (t >= timeout) {
                gui.error(error);
                return false;
            }
            try {
                Thread.sleep(HAND_DELAY);
            } catch (InterruptedException ie) {
                throw ie;
            }
        }
        return true;
    }

    public static boolean waitForProgressFinish(GameUI gui, int timeout, String error) throws InterruptedException {
        int t = 0;
        while (gui.prog == -1) {
            t += PROG_ACT_DELAY;
            if (t >= timeout)
                break;
            try {
                Thread.sleep(PROG_ACT_DELAY);
            } catch (InterruptedException ie) {
                throw ie;
            }
        }

        t = 0;
        while (gui.prog != -1) {
            t += PROG_FINISH_DELAY;
            if (t >= timeout) {
                gui.error(error);
                return false;
            }
            try {
                Thread.sleep(PROG_FINISH_DELAY);
            } catch (InterruptedException ie) {
                throw ie;
            }
        }
        return true;
    }

    public static boolean waitForOccupiedEquiporySlot(GameUI gui, int slot, int timeout, String error) throws InterruptedException {
        Equipory e = gui.getequipory();
        int t = 0;
        while (e.quickslots[slot] == null) {
            t += HAND_DELAY;
            if (t >= timeout) {
                gui.error(error);
                return false;
            }
            try {
                Thread.sleep(HAND_DELAY);
            } catch (InterruptedException ie) {
                throw ie;
            }
        }
        return true;
    }

    public static void drinkTillFull(GameUI gui, int threshold, int stoplevel) throws InterruptedException {
        while (gui.maininv.drink(threshold)) {
            Thread.sleep(490);
            do {
                Thread.sleep(10);
                IMeter.Meter stam = gui.getmeter("stam", 0);
                if (stam.a >= stoplevel)
                    break;
            } while (gui.prog >= 0);
        }
    }

    final protected static char[] hexArray = "0123456789ABCDEF".toCharArray();
    public static String bytesToHex(byte[] bytes) {
        char[] hexChars = new char[bytes.length * 2];
        for ( int j = 0; j < bytes.length; j++ ) {
            int v = bytes[j] & 0xFF;
            hexChars[j * 2] = hexArray[v >>> 4];
            hexChars[j * 2 + 1] = hexArray[v & 0x0F];
        }
        return new String(hexChars);
    }

    public static String prettyHexView(byte[] ba) {
        StringBuilder sb = new StringBuilder();
        Formatter formatter = new Formatter(sb);
        for (int j = 1; j < ba.length+1; j++) {
            if (j % 8 == 1 || j == 0) {
                if( j != 0){
                    sb.append("\n");
                }
                formatter.format("0%d\t|\t", j / 8);
            }
            formatter.format("%02X", ba[j-1]);
            if (j % 4 == 0) {
                sb.append(" ");
            }
        }
        sb.append("\n");
        return sb.toString();
    }
}
