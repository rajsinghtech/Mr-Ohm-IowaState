#include <stdio.h>
#include <stdint.h>

// #include "include/time.h"

#include <generated/csr.h>
#include <generated/mem.h>
#include <generated/git.h>

#include <system.h>

#include <bios/init.h>
#include <bios/readline.h>
#include <bios/helpers.h>
#include <bios/command.h>

#include <stdlib.h>



/**
 * Command "mem_read"
 *
 * Memory read
 *
 */
static void mem_read_handler(int nb_params, char **params)
{
	char *c;
	unsigned int *addr;
	unsigned int length;

	if (nb_params < 1) {
		printf("mem_read <address> [length]");
		return;
	}
	addr = (unsigned int *)strtoul(params[0], &c, 0);
	if (*c != 0) {
		printf("Incorrect address");
		return;
	}
	if (nb_params == 1) {
		length = 4;
	} else {
		length = strtoul(params[1], &c, 0);
		if(*c != 0) {
			printf("\nIncorrect length");
			return;
		}
	}
	dump_bytes(addr, length, (unsigned long)addr);
}


/**
 * Command "mem_write"
 *
 * Memory write
 *
 */
static void mem_write_handler(int nb_params, char **params)
{
	char *c;
	void *addr;
	unsigned int value;
	unsigned int count;
	unsigned int size;
	unsigned int i;

	if (nb_params < 2) {
		printf("mem_write <address> <value> [count] [size]");
		return;
	}

	size = 4;
	addr = (void *)strtoul(params[0], &c, 0);

	if (*c != 0) {
		printf("Incorrect address");
		return;
	}

	value = strtoul(params[1], &c, 0);
	if(*c != 0) {
		printf("Incorrect value");
		return;
	}

	if (nb_params == 2) {
		count = 1;
	} else {
		count = strtoul(params[2], &c, 0);
		if(*c != 0) {
			printf("Incorrect count");
			return;
		}
	}

	if (nb_params == 4)
		size = strtoul(params[3], &c, 0);

	for (i = 0; i < count; i++) {
		switch (size) {
		case 1:
			*(uint8_t *)addr = value;
			addr += 1;
			break;
		case 2:
			*(uint16_t *)addr = value;
			addr += 2;
			break;
		case 4:
			*(uint32_t *)addr = value;
			addr += 4;
			break;
		default:
			printf("Incorrect size");
			return;
		}
	}
}


/**
 * Main function
 */
int main(int argc, char **argv)
{
    char buffer[CMD_LINE_BUFFER_SIZE];
    char *command, *params[8];
    int nb_params;
    struct command_struct *cmd;

    while (1) {
        readline(buffer, CMD_LINE_BUFFER_SIZE);
        if (buffer[0] != 0) {
            printf("\n");
            nb_params = get_param(buffer, &command, params);
            cmd = command_dispatcher(command, nb_params, params);
            if (!strcmp(command, "mem_read")) {
                mem_read_handler(nb_params, params);
            } else if (!strcmp(command, "mem_write")) {
                mem_write_handler(nb_params, params);
            }
        }
        printf("\n%s", PROMPT);
    }

    return 0;
}