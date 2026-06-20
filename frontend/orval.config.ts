import { defineConfig } from "orval";

export default defineConfig({
  quickfit: {
    input: {
      target: "http://localhost:8000/api/openapi.json", // maybe env variable instead?
    },
    output: {
      mode: "tags-split",
      target: "src/api/generated",
      client: "react-query",
      override: {
        mutator: {
          path: "src/api/client.ts",
          name: "customFetch",
        },
      },
    },
  },
});
