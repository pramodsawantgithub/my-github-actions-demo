async function run() {
  const exec = await import('@actions/exec');
  await exec.exec('node', ['--version']);
}

if (require.main === module) {
  run().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}

module.exports = {
  run,
};