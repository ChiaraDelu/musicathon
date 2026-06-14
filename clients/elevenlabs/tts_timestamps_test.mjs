import { ElevenLabsClient } from '@elevenlabs/elevenlabs-js';
import { writeFile } from 'fs/promises';
import 'dotenv/config';

const elevenlabs = new ElevenLabsClient({
  apiKey: process.env.ELEVENLABS_API_KEY,
});

const result = await elevenlabs.textToSpeech.convertWithTimestamps(
  'JBFqnCBsd6RMkjVDRZzb', // voice_id (default voice)
  {
    text: 'The first move is what sets everything in motion.',
    modelId: 'eleven_multilingual_v2',
    outputFormat: 'mp3_44100_128',
  }
);

// Salva l'audio decodificando il base64
const audioBuffer = Buffer.from(result.audioBase64, 'base64');
await writeFile('output_timestamps.mp3', audioBuffer);

// Salva l'allineamento (timestamp per ogni carattere)
await writeFile('alignment.json', JSON.stringify(result.alignment, null, 2));

console.log('Audio salvato in output_timestamps.mp3');
console.log('Allineamento salvato in alignment.json');
console.log('\nPrimi 10 caratteri con timestamp:');
const { characters, characterStartTimesSeconds, characterEndTimesSeconds } = result.alignment;
for (let i = 0; i < Math.min(10, characters.length); i++) {
  console.log(`  "${characters[i]}" -> ${characterStartTimesSeconds[i]}s - ${characterEndTimesSeconds[i]}s`);
}
