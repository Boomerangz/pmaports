import java.lang.reflect.Method;

/* Plays beeps as a voice-communication stream so that the Android audio
 * policy and HAL pick the handset (earpiece) route themselves. */
public class EarTest {
    public static void main(String[] a) throws Exception {
        int secs = a.length > 0 ? Integer.parseInt(a[0]) : 10;
        int usage = a.length > 1 ? Integer.parseInt(a[1]) : 2; /* 2 = USAGE_VOICE_COMMUNICATION, 1 = MEDIA */
        Class<?> AAB = Class.forName("android.media.AudioAttributes$Builder");
        Object b = AAB.getDeclaredConstructor().newInstance();
        AAB.getMethod("setUsage", int.class).invoke(b, usage);
        AAB.getMethod("setContentType", int.class).invoke(b, usage == 2 ? 1 : 2);
        Object attrs = AAB.getMethod("build").invoke(b);
        Class<?> AFB = Class.forName("android.media.AudioFormat$Builder");
        Object fb = AFB.getDeclaredConstructor().newInstance();
        AFB.getMethod("setSampleRate", int.class).invoke(fb, 48000);
        AFB.getMethod("setEncoding", int.class).invoke(fb, 2);
        AFB.getMethod("setChannelMask", int.class).invoke(fb, 4);
        Object fmt = AFB.getMethod("build").invoke(fb);
        Class<?> AT = Class.forName("android.media.AudioTrack");
        Class<?> AA = Class.forName("android.media.AudioAttributes");
        Class<?> AF = Class.forName("android.media.AudioFormat");
        Object t = AT.getConstructor(AA, AF, int.class, int.class, int.class)
                     .newInstance(attrs, fmt, 48000 * 2, 1, 0);
        System.out.println("track state " + AT.getMethod("getState").invoke(t));
        AT.getMethod("play").invoke(t);
        short[] s = new short[48000];
        for (int i = 0; i < 24000; i++)
            s[i] = (short) (12000 * Math.sin(2 * Math.PI * 440 * i / 48000.0));
        Method w = AT.getMethod("write", short[].class, int.class, int.class);
        for (int k = 0; k < secs; k++) {
            Object r = w.invoke(t, s, 0, s.length);
            if (k == 0) System.out.println("first write " + r);
        }
        Thread.sleep(500);
        AT.getMethod("stop").invoke(t);
        AT.getMethod("release").invoke(t);
        System.out.println("done");
    }
}
