// Central API configuration. Change `DEVICE_IP` to your machine's IP on the local network
// (e.g. "192.168.1.100") when testing on a physical device. Keep the port if needed.
const DEVICE_IP = "http://192.168.137.199:8000"; // default for Android emulator; change for physical device

export const BASE_URL = DEVICE_IP;

export default {
  BASE_URL,
};
