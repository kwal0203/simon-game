import { defineConfig } from 'vite';

export default defineConfig({
    server: {
        host: true,
        allowedHosts: ["electricincubator.com", "www.electricincubator.com"]
    }
});
