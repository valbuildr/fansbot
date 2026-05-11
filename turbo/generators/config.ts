import { PlopTypes } from "@turbo/gen";

export default function generator(plop: PlopTypes.NodePlopAPI): void {
  plop.setGenerator("pkg", {
    description:
      "Creates a new packaage and sets up eslint.",
    prompts: [
      {
        type: "input",
        name: "package",
        message: "What is the name of the new package to create?",
        validate: (input: string) => {
          if (input.includes(".")) {
            return "package name cannot include an extension";
          }
          if (input.includes(" ")) {
            return "package name cannot include spaces";
          }
          if (input.includes("/")) {
            return "package name cannot include slashes";
          }
          if (!input) {
            return "package name is required";
          }
          return true;
        }
      }
    ],
    actions: [
      {
        type: "add",
        path: "{{ turbo.paths.root }}/packages/{{ dashCase package }}/package.json",
        templateFile: "templates/pkg-package.hbs",
        skipIfExists: true
      },
      {
        type: "add",
        path: "{{ turbo.paths.root }}/packages/{{ dashCase package }}/src/index.ts",
        templateFile: "templates/pkg-index.hbs",
        skipIfExists: true
      },
      {
        type: "add",
        path: "{{ turbo.paths.root }}/packages/{{ dashCase package }}/eslint.config.mjs",
        templateFile: "templates/pkg-eslint.hbs",
        skipIfExists: true
      },
      {
        type: "add",
        path: "{{ turbo.paths.root }}/packages/{{ dashCase package }}/tsconfig.json",
        templateFile: "templates/pkg-tsconfig.hbs",
        skipIfExists: true
      },
      function promptInstall(answers: { package: string }) {
        return `Set up packages/${answers.package}! Lastly, run 'bun install' to install dependencies and add @fansbot/${answers.package} to bun.lock.`;
      }
    ]
  });
  plop.setGenerator("app", {
    description:
      "Creates a new app and sets up eslint.",
    prompts: [
      {
        type: "input",
        name: "app",
        message: "What is the name of the new app to create?",
        validate: (input: string) => {
          if (input.includes(".")) {
            return "app name cannot include an extension";
          }
          if (input.includes(" ")) {
            return "app name cannot include spaces";
          }
          if (input.includes("/")) {
            return "app name cannot include slashes";
          }
          if (!input) {
            return "app name is required";
          }
          return true;
        }
      }
    ],
    actions: [
      {
        type: "add",
        path: "{{ turbo.paths.root }}/apps/{{ dashCase app }}/package.json",
        templateFile: "templates/app-package.hbs",
        skipIfExists: true
      },
      {
        type: "add",
        path: "{{ turbo.paths.root }}/apps/{{ dashCase app }}/src/index.ts",
        templateFile: "templates/app-index.hbs",
        skipIfExists: true
      },
      {
        type: "add",
        path: "{{ turbo.paths.root }}/apps/{{ dashCase app }}/eslint.config.mjs",
        templateFile: "templates/app-eslint.hbs",
        skipIfExists: true
      },
      {
        type: "add",
        path: "{{ turbo.paths.root }}/apps/{{ dashCase app }}/tsconfig.json",
        templateFile: "templates/app-tsconfig.hbs",
        skipIfExists: true
      },
      function promptInstall(answers: { app: string }) {
        return `Set up apps/${answers.app}! Lastly, run 'bun install' to install dependencies and add ${answers.app} to bun.lock.`;
      }
    ]
  })
}
