// esbuild.js - CommonJS puro (Node.js 25+ compatível)
const esbuild = require('esbuild');

const production = process.argv.includes('--production');
const watch = process.argv.includes('--watch');

async function build() {
    const context = await esbuild.context({
        entryPoints: ['src/extension.ts'],
        bundle: true,
        external: ['vscode'],
        format: 'cjs',
        target: 'node18',
        logLevel: "info",
        sourcemap: production ? false : 'inline',
        treeShaking: true,
        outfile: 'dist/extension.js',
        loader: {
            '.ts': 'ts'
        }
    });

    if (watch) {
        await context.watch();
        console.log('👀 Watching for changes...');
        require('util').print('Press Ctrl+C to stop\n');
    } else {
        await context.rebuild();
        await context.dispose();
        console.log('✅ Build complete: dist/extension.js');
    }
}

build().catch(err => {
    console.error('❌ Build failed:', err);
    process.exit(1);
});
