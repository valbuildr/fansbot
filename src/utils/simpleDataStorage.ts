import * as path from "node:path";

export async function writeToStorage(ext: string, folder: string, fileName: string, content: string): Promise<void> {
    await Bun.write(path.join(process.cwd(), "data", ext, folder, `${fileName}.txt`), content);
}

export async function readFromStorage(ext: string, folder: string, fileName: string): Promise<string | null> {
    const f = Bun.file(path.join(process.cwd(), "data", ext, folder, `${fileName}.txt`));
    if (await f.exists()) {
        return await f.text();
    } else {
        return null;
    }
}