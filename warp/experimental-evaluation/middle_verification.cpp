#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <sys/random.h>
#include <random>
#include <mutex>
#include <atomic>

#include "warp.h"

std::mutex stdout_mutex;

void convert_hexstr_to_statearray(const char *hex_str, int dx[32])
{
  for (int i = 0; i < 32; i++)
  {
    char hex[2];
    hex[0] = hex_str[i];
    hex[1] = '\0';
    dx[i] = (int)(strtol(hex, NULL, 16) & 0xf);
  }
}


int main()
{
  const char *pt_delta_str = "0000000000000000000000000000000a";
  const char *ct_delta_str = "00000000000000000a00000000000000";
  int pt_delta[32];
  int ct_delta[32];
  int num_rounds = 10;

  setvbuf(stdout, NULL, _IONBF, 0);
  convert_hexstr_to_statearray(pt_delta_str, pt_delta);
  convert_hexstr_to_statearray(ct_delta_str, ct_delta);

  size_t numkeys = 1<<8;
  size_t trials_per_key = 1<<14;

  printf("analyzing 2^%.1f queries * 2^%.1f keys of the follwoing boomerang for %d rounds\n",
         log2(trials_per_key), log2(numkeys), num_rounds);
  printf("%s\n", pt_delta_str);
  printf("%s\n", ct_delta_str);

  std::atomic_size_t total_success(0);
  double max_prob = -std::numeric_limits<double>::infinity(), min_prob = std::numeric_limits<double>::infinity();

#pragma omp parallel for
  for (size_t key_ctr = 0; key_ctr < numkeys; ++key_ctr)
  {
    std::random_device r;
    int key[32];
    getrandom(&key, sizeof(key), 0);
    for (size_t i = 0; i < sizeof(key) / sizeof(*key); ++i)
      key[i] &= 0xF;

    std::seed_seq seed2{r(), r(), r(), r(), r(), r(), r(), r()};
    std::mt19937 mt(seed2);
    std::uniform_int_distribution<int> distr(0, 15);

    size_t successful_cnt = 0;
    for (size_t trial_ctr = 0; trial_ctr < trials_per_key; ++trial_ctr)
    {
      int pt1[32], pt2[32], pt3[32], pt4[32];
      int ct1[32], ct2[32], ct3[32], ct4[32];
      for (size_t i = 0; i < sizeof(pt1) / sizeof(*pt1); ++i)
      {
        pt1[i] = distr(mt);
        pt2[i] = pt1[i] ^ pt_delta[i];
      }

      enc(pt1, ct1, key, num_rounds);
      enc(pt2, ct2, key, num_rounds);
      for (size_t i = 0; i < sizeof(pt1) / sizeof(*pt1); ++i)
      {
        ct3[i] = ct1[i] ^ ct_delta[i];
        ct4[i] = ct2[i] ^ ct_delta[i];
      }
      dec(pt3, ct3, key, num_rounds);
      dec(pt4, ct4, key, num_rounds);

      bool trial_successful = true;
      for (size_t i = 0; i < sizeof(pt1) / sizeof(*pt1); ++i)
      {
        if ((pt3[i] ^ pt4[i]) != pt_delta[i])
        {
          trial_successful = false;
          break;
        }
      }
      successful_cnt += trial_successful ? 1 : 0;
    }

    total_success += successful_cnt;

    double prob = (double) successful_cnt / (double) trials_per_key;
    std::lock_guard<std::mutex> guard(stdout_mutex);
    if (prob > max_prob)
      max_prob = prob;
    if (prob < min_prob)
      min_prob = prob;
    printf("key: ");
    for (size_t i = 0; i < 32; ++i)
      printf("%01x", key[i]);
    printf(": 2^%.3f (%zd/%zd)\n", log2(prob), successful_cnt, trials_per_key);
  }
  double prob = (double) total_success.load() / (double) (numkeys * trials_per_key);
  printf("overall: 2^%.3f (%zd/%zd)\n", log2(prob), total_success.load(), numkeys * trials_per_key);
  printf("range:   2^%.3f ... 2^%.3f\n", log2(min_prob), log2(max_prob));
}
