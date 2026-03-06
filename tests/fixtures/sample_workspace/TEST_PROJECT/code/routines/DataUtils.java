package routines;

/**
 * Utility routine for common data transformations.
 */
public class DataUtils {

    /**
     * Normalize a string: trim, lowercase, remove extra whitespace.
     */
    public static String normalize(String input) {
        if (input == null) return null;
        return input.trim().toLowerCase().replaceAll("\\s+", " ");
    }

    /**
     * Mask an email address for privacy.
     * "user@example.com" → "u***@example.com"
     */
    public static String maskEmail(String email) {
        if (email == null || !email.contains("@")) return email;
        String[] parts = email.split("@");
        String local = parts[0];
        if (local.length() <= 1) return email;
        return local.charAt(0) + "***@" + parts[1];
    }

    /**
     * Check if a string is null or empty after trimming.
     */
    public static boolean isBlank(String s) {
        return s == null || s.trim().isEmpty();
    }
}
