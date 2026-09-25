package aiia.plugin.common;

import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.Base64;
import java.util.Collections;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import kotlinx.serialization.json.JsonElement;
import kotlinx.serialization.json.JsonObject;
import kotlinx.serialization.json.JsonPrimitive;

public final class PluginSupport {
    private static final Pattern NUMBER = Pattern.compile("-?\\d+(?:\\.\\d+)?");
    private static final SecureRandom RANDOM = new SecureRandom();
    private static final DateTimeFormatter ISO =
            DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss'Z'").withZone(ZoneOffset.UTC);

    private PluginSupport() {
    }

    public static JsonObject schema() {
        return new JsonObject(Collections.emptyMap());
    }

    public static String argument(JsonObject arguments, String key) {
        if (arguments == null) return "";
        JsonElement value = arguments.get(key);
        if (value instanceof JsonPrimitive) return ((JsonPrimitive) value).getContent();
        return value == null ? "" : value.toString();
    }

    public static String execute(String operation, String tool, JsonObject arguments) {
        try {
            String text = argument(arguments, "text");
            switch (operation) {
                case "uppercase":
                    return text.toUpperCase(Locale.ROOT);
                case "lowercase":
                    return text.toLowerCase(Locale.ROOT);
                case "reverse":
                    return new StringBuilder(text).reverse().toString();
                case "word_count":
                    return Integer.toString(text.trim().isEmpty() ? 0 : text.trim().split("\\s+").length);
                case "json_summary": {
                    long keys = text.lines().flatMap(line -> java.util.Arrays.stream(line.split("\""))).skip(1).count();
                    return "characters=" + text.length() + ", lines=" + text.lines().count() + ", quotedTokens=" + keys;
                }
                case "base64_encode":
                    return Base64.getEncoder().encodeToString(text.getBytes(StandardCharsets.UTF_8));
                case "base64_decode":
                    return new String(Base64.getDecoder().decode(text), StandardCharsets.UTF_8);
                case "sha256":
                    return hex(MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)));
                case "md5":
                    return hex(MessageDigest.getInstance("MD5").digest(text.getBytes(StandardCharsets.UTF_8)));
                case "url_summary": {
                    URI uri = URI.create(text);
                    return "scheme=" + value(uri.getScheme()) + ", host=" + value(uri.getHost()) +
                            ", path=" + value(uri.getPath()) + ", query=" + value(uri.getQuery());
                }
                case "datetime": {
                    String raw = text.trim();
                    long millis = raw.isEmpty() ? System.currentTimeMillis() : Long.parseLong(raw);
                    return ISO.format(Instant.ofEpochMilli(millis));
                }
                case "color_hex": {
                    String hex = text.trim().replace("#", "");
                    if (hex.length() != 6) return "error: expected #RRGGBB";
                    int red = Integer.parseInt(hex.substring(0, 2), 16);
                    int green = Integer.parseInt(hex.substring(2, 4), 16);
                    int blue = Integer.parseInt(hex.substring(4, 6), 16);
                    return "rgb(" + red + ", " + green + ", " + blue + ")";
                }
                case "length": {
                    double value = number(arguments, "value");
                    String unit = argument(arguments, "unit").toLowerCase(Locale.ROOT);
                    if (unit.equals("m") || unit.isEmpty()) return format(value) + " m = " + format(value * 1000) + " mm";
                    if (unit.equals("km")) return format(value) + " km = " + format(value * 1000) + " m";
                    if (unit.equals("mi")) return format(value) + " mi = " + format(value * 1.609344) + " km";
                    if (unit.equals("ft")) return format(value) + " ft = " + format(value * 0.3048) + " m";
                    return "error: supported units: m, km, mi, ft";
                }
                case "weight": {
                    double value = number(arguments, "value");
                    String unit = argument(arguments, "unit").toLowerCase(Locale.ROOT);
                    if (unit.equals("kg") || unit.isEmpty()) return format(value) + " kg = " + format(value * 2.2046226) + " lb";
                    if (unit.equals("lb")) return format(value) + " lb = " + format(value / 2.2046226) + " kg";
                    if (unit.equals("g")) return format(value) + " g = " + format(value / 1000) + " kg";
                    return "error: supported units: kg, lb, g";
                }
                case "temperature": {
                    double value = number(arguments, "value");
                    String unit = argument(arguments, "unit").toUpperCase(Locale.ROOT);
                    if (unit.equals("C") || unit.isEmpty()) return format(value) + " °C = " + format(value * 9 / 5 + 32) + " °F";
                    if (unit.equals("F")) return format(value) + " °F = " + format((value - 32) * 5 / 9) + " °C";
                    return "error: supported units: C, F";
                }
                case "number_stats": {
                    Matcher matcher = NUMBER.matcher(text);
                    double sum = 0;
                    int count = 0;
                    double min = Double.POSITIVE_INFINITY;
                    double max = Double.NEGATIVE_INFINITY;
                    while (matcher.find()) {
                        double value = Double.parseDouble(matcher.group());
                        sum += value;
                        count++;
                        min = Math.min(min, value);
                        max = Math.max(max, value);
                    }
                    return count == 0 ? "count=0" : "count=" + count + ", min=" + format(min) + ", max=" + format(max) + ", avg=" + format(sum / count);
                }
                case "password_generate": {
                    int length = (int) Math.max(8, Math.min(64, number(arguments, "length")));
                    String alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%";
                    StringBuilder result = new StringBuilder(length);
                    for (int i = 0; i < length; i++) result.append(alphabet.charAt(RANDOM.nextInt(alphabet.length())));
                    return result.toString();
                }
                case "slugify":
                    return text.toLowerCase(Locale.ROOT)
                            .replaceAll("[^a-z0-9]+", "-")
                            .replaceAll("(^-|-$)", "");
                case "markdown_clean":
                    return text.replaceAll("[`*_>#]", "").replaceAll("\\[([^]]+)]\\([^)]*\\)", "$1").trim();
                case "random_choice": {
                    String[] choices = text.split("\\|");
                    return choices.length == 0 ? "" : choices[RANDOM.nextInt(choices.length)].trim();
                }
                case "contact_mask": {
                    int at = text.indexOf('@');
                    if (at > 1) return text.charAt(0) + "***" + text.substring(at);
                    if (text.length() > 4) return text.substring(0, 2) + "***" + text.substring(text.length() - 2);
                    return "***";
                }
                case "text_profile": {
                    long letters = text.chars().filter(Character::isLetter).count();
                    long digits = text.chars().filter(Character::isDigit).count();
                    long spaces = text.chars().filter(Character::isWhitespace).count();
                    return "letters=" + letters + ", digits=" + digits + ", spaces=" + spaces + ", chars=" + text.length();
                }
                default:
                    return "error: unknown operation " + operation;
            }
        } catch (Exception error) {
            return "error: " + error.getMessage();
        }
    }

    private static double number(JsonObject arguments, String key) {
        String value = argument(arguments, key);
        return value.isBlank() ? 0 : Double.parseDouble(value);
    }

    private static String format(double value) {
        return String.format(Locale.US, "%.4f", value).replaceAll("\\.0+$", "").replaceAll("(\\.\\d*?)0+$", "$1");
    }

    private static String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) result.append(String.format(Locale.US, "%02x", value & 0xff));
        return result.toString();
    }

    private static String value(String value) {
        return value == null ? "" : value;
    }
}
