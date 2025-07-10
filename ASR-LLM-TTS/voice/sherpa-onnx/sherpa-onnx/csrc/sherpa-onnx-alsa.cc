#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <algorithm>
#include <cctype>
#include <cstdint>
#include <chrono>
#include <thread>
#include "sherpa-onnx/csrc/alsa.h"
#include "sherpa-onnx/csrc/display.h"
#include "sherpa-onnx/csrc/online-recognizer.h"
#include "sherpa-onnx/csrc/parse-options.h"
#include "ZmqClient.h"  // Add ZMQ support

bool stop = false;
bool wait = false;
static void Handler(int sig) {
  stop = true;
  fprintf(stderr, "\nCaught Ctrl + C. Exiting...\n");
}

int main(int32_t argc, char *argv[]) {
  signal(SIGINT, Handler);
  
  // Add ZeroMQ clients (like in the microphone code)
  zmq_component::ZmqClient client;
  zmq_component::ZmqClient block_client("tcp://localhost:6677");

  const char *kUsageMessage = R"usage(...)usage";  // Keep original usage message

  sherpa_onnx::ParseOptions po(kUsageMessage);
  sherpa_onnx::OnlineRecognizerConfig config;
  config.Register(&po);
  po.Read(argc, argv);
  
  if (po.NumArgs() != 1) {
    fprintf(stderr, "Please provide only 1 argument: the device name\n");
    po.PrintUsage();
    exit(EXIT_FAILURE);
  }

  sherpa_onnx::OnlineRecognizer recognizer(config);
  int32_t expected_sample_rate = config.feat_config.sampling_rate;
  std::string device_name = po.GetArg(1);
  sherpa_onnx::Alsa alsa(device_name.c_str());

  if (alsa.GetExpectedSampleRate() != expected_sample_rate) {
    fprintf(stderr, "Sample rate mismatch: %d != %d\n", 
            alsa.GetExpectedSampleRate(), expected_sample_rate);
    exit(-1);
  }

  int32_t chunk = 0.1 * alsa.GetActualSampleRate();
  auto stream = recognizer.CreateStream();
  sherpa_onnx::Display display;
  int32_t segment_index = 0;
  std::string last_text;

  while (!stop) {
    const std::vector<float> &samples = alsa.Read(chunk);
    stream->AcceptWaveform(expected_sample_rate, samples.data(), samples.size());

    while (recognizer.IsReady(stream.get())) {
      recognizer.DecodeStream(stream.get());
    }

    auto text = recognizer.GetResult(stream.get()).text;
    bool is_endpoint = recognizer.IsEndpoint(stream.get());

    if (is_endpoint && !config.model_config.paraformer.encoder.empty()) {
      std::vector<float> tail_paddings(static_cast<int>(1.0 * expected_sample_rate));
      stream->AcceptWaveform(expected_sample_rate, tail_paddings.data(), tail_paddings.size());
      while (recognizer.IsReady(stream.get())) {
        recognizer.DecodeStream(stream.get());
      }
      text = recognizer.GetResult(stream.get()).text;
    }

    if (!text.empty() && last_text != text) {
      last_text = text;
      std::transform(text.begin(), text.end(), text.begin(), [](auto c) { return std::tolower(c); });
      display.Print(segment_index, text);
      fflush(stderr);
    }

    if (is_endpoint) {
      if (!text.empty()) {
        // Send recognized text to LLM via ZMQ (like in the microphone code)
        auto response = client.request(text);
        std::cout << "[LLM -> Voice] Response: " << response << std::endl;

        // Block TTS while processing (optional)
        wait = true;
        auto block_response = block_client.request("block");
        std::cout << "[TTS -> Voice] Block response: " << block_response << std::endl;
        wait = false;

        segment_index++;
      }
      recognizer.Reset(stream.get());
    }
    
  
   
  }
  return 0;
}
