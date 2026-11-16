/* Diagnostic: publish a range of QRTR service IDs and log whatever is sent to them. */
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <libqrtr.h>

int main(int argc, char **argv)
{
	int lo = atoi(argv[1]), hi = atoi(argv[2]);
	int n = hi - lo + 1, i, ret;
	struct pollfd *pfd = calloc(n, sizeof(*pfd));
	struct sockaddr_qrtr sq;
	struct qrtr_packet pkt;
	unsigned char buf[8192];
	socklen_t sl;

	setvbuf(stdout, NULL, _IOLBF, 0);
	for (i = 0; i < n; i++) {
		pfd[i].fd = -1;
		if (argc > 3 && strstr(argv[3], "skip") && lo + i >= 227 && lo + i <= 229)
			continue;
		pfd[i].fd = qrtr_open(0);
		pfd[i].events = POLLIN;
		if (pfd[i].fd < 0 || qrtr_publish(pfd[i].fd, lo + i, 1, 0) < 0) {
			fprintf(stderr, "publish %d failed\n", lo + i);
			return 1;
		}
	}
	printf("trap: published %d..%d\n", lo, hi);
	for (;;) {
		if (poll(pfd, n, -1) < 0)
			return 1;
		for (i = 0; i < n; i++) {
			if (pfd[i].fd < 0 || !(pfd[i].revents & POLLIN))
				continue;
			sl = sizeof(sq);
			ret = recvfrom(pfd[i].fd, buf, sizeof(buf), 0, (void *)&sq, &sl);
			if (ret < 0)
				continue;
			if (qrtr_decode(&pkt, buf, ret, &sq) < 0 || pkt.type != QRTR_TYPE_DATA)
				continue;
			printf("svc %d from %u:%u len %zu:", lo + i, pkt.node, pkt.port, pkt.data_len);
			for (ret = 0; ret < (int)pkt.data_len && ret < 48; ret++)
				printf(" %02x", ((unsigned char *)pkt.data)[ret]);
			printf("\n");
		}
	}
}
